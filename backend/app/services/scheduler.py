"""Scheduler service for running scheduled scrape jobs."""

import asyncio
import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.scrape_job import ScrapeJobCreate, ScrapeJobOptions
from app.repositories.project import ProjectRepository
from app.repositories.schedule import ScheduleRepository
from app.repositories.scrape_job import ScrapeJobRepository
from app.services.scrape_executor import get_job_queue

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled scrape jobs."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.project_repo = ProjectRepository(db)
        self.job_repo = ScrapeJobRepository(db)
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the scheduler service."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler service started")

    async def stop(self) -> None:
        """Stop the scheduler service."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler service stopped")

    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._process_due_schedules()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")

            # Check every minute
            await asyncio.sleep(60)

    async def _process_due_schedules(self) -> None:
        """Process all schedules that are due to run."""
        schedules = await self.schedule_repo.get_due_schedules()

        for schedule in schedules:
            try:
                await self._execute_schedule(schedule)
            except Exception as e:
                logger.error(f"Error executing schedule {schedule.id}: {e}")
                await self.schedule_repo.record_execution(
                    schedule_id=schedule.id,
                    job_id=None,
                    status="failed",
                    error=str(e),
                )

    async def _execute_schedule(self, schedule) -> None:
        """Execute a single schedule."""
        logger.info(f"Executing schedule {schedule.id} for project {schedule.project_id}")

        # Get project
        try:
            project = await self.project_repo.get_project(
                schedule.project_id, schedule.user_id
            )
        except Exception:
            logger.error(f"Project {schedule.project_id} not found, skipping schedule")
            await self.schedule_repo.record_execution(
                schedule_id=schedule.id,
                job_id=None,
                status="skipped",
                error="Project not found",
            )
            return

        # Create scrape job
        job_data = ScrapeJobCreate(
            target_ids=None,  # All targets
            options=ScrapeJobOptions(
                max_results=project.config.limits.max_reviews_per_target,
            ),
        )

        try:
            job = await self.job_repo.create_job(
                project_id=schedule.project_id,
                user_id=schedule.user_id,
                job_data=job_data,
                trigger="scheduled",
            )

            # Enqueue job
            job_queue = await get_job_queue(self.db)
            await job_queue.enqueue(job, project)

            await self.schedule_repo.record_execution(
                schedule_id=schedule.id,
                job_id=job.id,
                status="running",
            )

            logger.info(f"Scheduled job {job.id} created for schedule {schedule.id}")

        except Exception as e:
            logger.error(f"Failed to create job for schedule {schedule.id}: {e}")
            await self.schedule_repo.record_execution(
                schedule_id=schedule.id,
                job_id=None,
                status="failed",
                error=str(e),
            )

    async def run_now(self, project_id: str, user_id: str) -> str:
        """Manually trigger a scheduled job now."""
        schedule = await self.schedule_repo.get_schedule(project_id, user_id)
        project = await self.project_repo.get_project(project_id, user_id)

        job_data = ScrapeJobCreate(
            target_ids=None,
            options=ScrapeJobOptions(
                max_results=project.config.limits.max_reviews_per_target,
            ),
        )

        job = await self.job_repo.create_job(
            project_id=project_id,
            user_id=user_id,
            job_data=job_data,
            trigger="manual",
        )

        job_queue = await get_job_queue(self.db)
        await job_queue.enqueue(job, project)

        return job.id


# Global scheduler instance
_scheduler: SchedulerService | None = None


async def get_scheduler(db: AsyncIOMotorDatabase) -> SchedulerService:
    """Get or create the scheduler service."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService(db)
        await _scheduler.start()
    return _scheduler


async def shutdown_scheduler() -> None:
    """Shutdown the scheduler service."""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None
