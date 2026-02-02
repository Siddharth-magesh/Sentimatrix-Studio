"""Scrape job repository for database operations."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.scrape_job import (
    ScrapeJob,
    ScrapeJobCreate,
    ScrapeJobList,
    ScrapeJobStats,
    TargetJobStatus,
)
from app.repositories.base import BaseRepository


class ScrapeJobRepository(BaseRepository):
    """Repository for scrape job database operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "scrape_jobs")
        self.targets_collection = db["targets"]

    async def create_job(
        self,
        project_id: str,
        user_id: str,
        job_data: ScrapeJobCreate,
        trigger: str = "manual",
    ) -> ScrapeJob:
        """Create a new scrape job."""
        # Get target IDs - either specified or all project targets
        if job_data.target_ids:
            target_ids = job_data.target_ids
        else:
            # Get all active targets for the project
            cursor = self.targets_collection.find(
                {
                    "project_id": project_id,
                    "user_id": user_id,
                    "status": "active",
                },
                {"_id": 1},
            )
            targets = await cursor.to_list(length=None)
            target_ids = [str(t["_id"]) for t in targets]

        if not target_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active targets found for this project",
            )

        # Create target job statuses
        target_statuses = [
            TargetJobStatus(target_id=tid).model_dump() for tid in target_ids
        ]

        now = datetime.now(timezone.utc)
        job_doc = {
            "project_id": project_id,
            "user_id": user_id,
            "status": "queued",
            "progress": 0,
            "targets": target_statuses,
            "options": job_data.options.model_dump(),
            "stats": ScrapeJobStats(targets_total=len(target_ids)).model_dump(),
            "trigger": trigger,
            "triggered_by": user_id,
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(job_doc)
        job_doc["id"] = str(result.inserted_id)
        del job_doc["_id"] if "_id" in job_doc else None

        return ScrapeJob(**job_doc)

    async def get_job(self, job_id: str, user_id: str) -> ScrapeJob:
        """Get a scrape job by ID."""
        job = await self.collection.find_one(
            {"_id": ObjectId(job_id), "user_id": user_id}
        )
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape job not found",
            )
        return self._doc_to_model(job, ScrapeJob)

    async def get_jobs_by_project(
        self,
        project_id: str,
        user_id: str,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ScrapeJobList:
        """Get paginated scrape jobs for a project."""
        query: dict[str, Any] = {"project_id": project_id, "user_id": user_id}
        if status_filter:
            query["status"] = status_filter

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        jobs = await cursor.to_list(length=page_size)

        return ScrapeJobList(
            items=[self._doc_to_model(j, ScrapeJob) for j in jobs],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        error_message: str | None = None,
    ) -> ScrapeJob:
        """Update job status."""
        update_doc: dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        }

        if status == "running":
            update_doc["started_at"] = datetime.now(timezone.utc)
        elif status in ("completed", "failed", "cancelled"):
            update_doc["completed_at"] = datetime.now(timezone.utc)

        if error_message:
            update_doc["error_message"] = error_message

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {"$set": update_doc},
            return_document=True,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape job not found",
            )

        return self._doc_to_model(result, ScrapeJob)

    async def update_job_progress(
        self,
        job_id: str,
        progress: int,
        stats: dict[str, Any] | None = None,
    ) -> None:
        """Update job progress and optionally stats."""
        update_doc: dict[str, Any] = {
            "progress": progress,
            "updated_at": datetime.now(timezone.utc),
        }

        if stats:
            for key, value in stats.items():
                update_doc[f"stats.{key}"] = value

        await self.collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_doc},
        )

    async def update_target_status(
        self,
        job_id: str,
        target_id: str,
        status: str,
        progress: int = 0,
        results_count: int = 0,
        error: str | None = None,
    ) -> None:
        """Update the status of a specific target in a job."""
        update_doc: dict[str, Any] = {
            "targets.$.status": status,
            "targets.$.progress": progress,
            "targets.$.results_count": results_count,
            "updated_at": datetime.now(timezone.utc),
        }

        if error:
            update_doc["targets.$.error"] = error

        await self.collection.update_one(
            {"_id": ObjectId(job_id), "targets.target_id": target_id},
            {"$set": update_doc},
        )

    async def cancel_job(self, job_id: str, user_id: str) -> ScrapeJob:
        """Cancel a running or queued job."""
        job = await self.get_job(job_id, user_id)

        if job.status not in ("queued", "running"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel job with status '{job.status}'",
            )

        return await self.update_job_status(job_id, "cancelled")

    async def get_running_jobs_count(self, user_id: str) -> int:
        """Get count of running jobs for a user."""
        return await self.collection.count_documents(
            {"user_id": user_id, "status": "running"}
        )

    async def get_queued_jobs(self, limit: int = 10) -> list[ScrapeJob]:
        """Get queued jobs for processing (oldest first)."""
        cursor = (
            self.collection.find({"status": "queued"})
            .sort("created_at", 1)
            .limit(limit)
        )
        jobs = await cursor.to_list(length=limit)
        return [self._doc_to_model(j, ScrapeJob) for j in jobs]

    async def increment_stats(
        self,
        job_id: str,
        field: str,
        amount: int = 1,
    ) -> None:
        """Increment a stats field."""
        await self.collection.update_one(
            {"_id": ObjectId(job_id)},
            {
                "$inc": {f"stats.{field}": amount},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )


def get_scrape_job_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ScrapeJobRepository:
    """Dependency for getting scrape job repository."""
    return ScrapeJobRepository(db)
