"""Scrape job execution service."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.project import Project
from app.models.result import Result, ResultContent, AnalysisResult
from app.models.scrape_job import ScrapeJob
from app.models.target import Target
from app.repositories.scrape_job import ScrapeJobRepository
from app.services.sentimatrix_service import SentimatrixService

logger = logging.getLogger(__name__)


class ScrapeExecutor:
    """Executes scrape jobs using Sentimatrix."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        job_repo: ScrapeJobRepository,
    ):
        self.db = db
        self.job_repo = job_repo
        self.results_collection = db["results"]
        self.targets_collection = db["targets"]
        self._cancelled = False

    async def execute_job(self, job: ScrapeJob, project: Project) -> None:
        """
        Execute a scrape job.

        Args:
            job: The scrape job to execute
            project: The project configuration
        """
        self._cancelled = False
        logger.info(f"Starting job {job.id} for project {project.id}")

        # Update job status to running
        await self.job_repo.update_job_status(job.id, "running")

        try:
            # Initialize Sentimatrix service with project config
            async with SentimatrixService(
                llm_config=project.config.llm,
                analysis_config=project.config.analysis,
                limits_config=project.config.limits,
                commercial_provider=project.config.scrapers.commercial_provider,
            ) as sm_service:
                # Process each target
                total_targets = len(job.targets)
                completed_targets = 0

                for target_status in job.targets:
                    if self._cancelled:
                        logger.info(f"Job {job.id} cancelled")
                        await self.job_repo.update_job_status(job.id, "cancelled")
                        return

                    target_id = target_status.target_id
                    logger.info(f"Processing target {target_id}")

                    try:
                        # Update target status
                        await self.job_repo.update_target_status(
                            job.id, target_id, "running"
                        )

                        # Get target details
                        target = await self._get_target(target_id)
                        if not target:
                            await self.job_repo.update_target_status(
                                job.id,
                                target_id,
                                "failed",
                                error="Target not found",
                            )
                            await self.job_repo.increment_stats(job.id, "errors_count")
                            continue

                        # Scrape target
                        results_count = await self._scrape_and_analyze_target(
                            job=job,
                            target=target,
                            project=project,
                            sm_service=sm_service,
                        )

                        # Update target status
                        await self.job_repo.update_target_status(
                            job.id,
                            target_id,
                            "completed",
                            progress=100,
                            results_count=results_count,
                        )
                        await self.job_repo.increment_stats(job.id, "targets_completed")
                        await self.job_repo.increment_stats(
                            job.id, "results_total", results_count
                        )

                    except Exception as e:
                        logger.error(f"Error processing target {target_id}: {e}")
                        await self.job_repo.update_target_status(
                            job.id,
                            target_id,
                            "failed",
                            error=str(e),
                        )
                        await self.job_repo.increment_stats(job.id, "errors_count")

                    # Update overall progress
                    completed_targets += 1
                    progress = int((completed_targets / total_targets) * 100)
                    await self.job_repo.update_job_progress(job.id, progress)

                    # Rate limiting between targets
                    await asyncio.sleep(project.config.limits.rate_limit_delay)

            # Job completed
            await self.job_repo.update_job_status(job.id, "completed")
            logger.info(f"Job {job.id} completed successfully")

        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            await self.job_repo.update_job_status(job.id, "failed", error_message=str(e))
            raise

    async def _get_target(self, target_id: str) -> Target | None:
        """Get target from database."""
        from bson import ObjectId

        doc = await self.targets_collection.find_one({"_id": ObjectId(target_id)})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return Target(**doc)

    async def _scrape_and_analyze_target(
        self,
        job: ScrapeJob,
        target: Target,
        project: Project,
        sm_service: SentimatrixService,
    ) -> int:
        """
        Scrape content from a target and analyze it.

        Returns:
            Number of results scraped and stored
        """
        # Scrape content
        scraped_data = await sm_service.scrape_url(
            url=target.url,
            platform=target.platform,
            max_results=job.options.max_results,
        )

        if not scraped_data:
            logger.warning(f"No data scraped from {target.url}")
            return 0

        # Process each scraped item
        results_stored = 0
        batch_texts = []
        batch_contents = []

        for raw_item in scraped_data:
            # Parse content
            content = sm_service.parse_scraped_content(raw_item)
            if not content.text:
                continue

            batch_texts.append(content.text)
            batch_contents.append(content)

            # Increment request count
            await self.job_repo.increment_stats(job.id, "requests_made")

        # Analyze in batch if we have texts
        if batch_texts:
            try:
                analyses = await sm_service.analyze_batch(batch_texts, batch_size=10)

                # Store results
                for content, analysis in zip(batch_contents, analyses):
                    await self._store_result(
                        job=job,
                        target=target,
                        content=content,
                        analysis=analysis,
                    )
                    results_stored += 1

            except Exception as e:
                logger.error(f"Batch analysis failed: {e}")
                # Fall back to storing without analysis
                for content in batch_contents:
                    await self._store_result(
                        job=job,
                        target=target,
                        content=content,
                        analysis=AnalysisResult(),
                    )
                    results_stored += 1

        return results_stored

    async def _store_result(
        self,
        job: ScrapeJob,
        target: Target,
        content: ResultContent,
        analysis: AnalysisResult,
    ) -> None:
        """Store a result in the database."""
        now = datetime.now(timezone.utc)

        # Calculate word count
        word_count = len(content.text.split()) if content.text else 0

        result_doc = {
            "project_id": job.project_id,
            "target_id": target.id,
            "user_id": job.user_id,
            "scrape_job_id": job.id,
            "content": content.model_dump(),
            "analysis": analysis.model_dump(),
            "platform": target.platform,
            "language": None,  # Could detect with langdetect
            "word_count": word_count,
            "created_at": now,
            "updated_at": now,
        }

        await self.results_collection.insert_one(result_doc)

    def cancel(self) -> None:
        """Cancel the current job execution."""
        self._cancelled = True


class JobQueue:
    """Simple in-memory job queue for processing scrape jobs."""

    def __init__(self, db: AsyncIOMotorDatabase, max_concurrent: int = 3):
        self.db = db
        self.max_concurrent = max_concurrent
        self._queue: asyncio.Queue[tuple[ScrapeJob, Project]] = asyncio.Queue()
        self._running: dict[str, ScrapeExecutor] = {}
        self._worker_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the job queue worker."""
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("Job queue started")

    async def stop(self) -> None:
        """Stop the job queue worker."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Job queue stopped")

    async def enqueue(self, job: ScrapeJob, project: Project) -> None:
        """Add a job to the queue."""
        await self._queue.put((job, project))
        logger.info(f"Job {job.id} enqueued")

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self._running:
            self._running[job_id].cancel()
            return True
        return False

    async def _worker(self) -> None:
        """Process jobs from the queue."""
        while True:
            try:
                # Wait for job
                job, project = await self._queue.get()

                # Wait if at capacity
                while len(self._running) >= self.max_concurrent:
                    await asyncio.sleep(1)

                # Execute job
                job_repo = ScrapeJobRepository(self.db)
                executor = ScrapeExecutor(self.db, job_repo)
                self._running[job.id] = executor

                try:
                    await executor.execute_job(job, project)
                finally:
                    del self._running[job.id]
                    self._queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")


# Global job queue instance
_job_queue: JobQueue | None = None


async def get_job_queue(db: AsyncIOMotorDatabase) -> JobQueue:
    """Get or create the job queue."""
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue(db)
        await _job_queue.start()
    return _job_queue


async def shutdown_job_queue() -> None:
    """Shutdown the job queue."""
    global _job_queue
    if _job_queue:
        await _job_queue.stop()
        _job_queue = None
