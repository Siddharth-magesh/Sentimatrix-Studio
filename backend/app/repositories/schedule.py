"""Schedule repository for database operations."""

from datetime import datetime, timezone, timedelta
from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.schedule import (
    Schedule,
    ScheduleCreate,
    ScheduleList,
    ScheduleUpdate,
    ScheduleExecution,
    ScheduleExecutionList,
)
from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository):
    """Repository for schedule database operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "schedules")
        self.executions_collection = db["schedule_executions"]

    def _calculate_next_run(
        self,
        frequency: str,
        schedule_time: str | None,
        day_of_week: int | None,
        day_of_month: int | None,
        tz_name: str = "UTC",
    ) -> datetime:
        """Calculate the next run time based on schedule configuration."""
        import pytz

        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)

        # Parse time if provided
        if schedule_time:
            hour, minute = map(int, schedule_time.split(":"))
        else:
            hour, minute = 9, 0  # Default 9:00 AM

        if frequency == "hourly":
            # Next hour at minute 0
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        elif frequency == "daily":
            # Today or tomorrow at specified time
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)

        elif frequency == "weekly":
            # Next occurrence of day_of_week at specified time
            target_day = day_of_week if day_of_week is not None else 0
            days_ahead = target_day - now.weekday()
            if days_ahead < 0 or (days_ahead == 0 and now.hour * 60 + now.minute >= hour * 60 + minute):
                days_ahead += 7
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=days_ahead)

        elif frequency == "monthly":
            # Next occurrence of day_of_month at specified time
            target_day = day_of_month if day_of_month is not None else 1
            next_run = now.replace(day=target_day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # Move to next month
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)

        else:
            next_run = now + timedelta(days=1)

        return next_run.astimezone(pytz.UTC).replace(tzinfo=None)

    async def create_schedule(
        self,
        user_id: str,
        schedule_data: ScheduleCreate,
    ) -> Schedule:
        """Create a new schedule."""
        now = datetime.now(timezone.utc)

        # Check if schedule already exists for this project
        existing = await self.collection.find_one(
            {"project_id": schedule_data.project_id, "user_id": user_id}
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Schedule already exists for this project",
            )

        # Calculate next run
        next_run = None
        if schedule_data.enabled:
            next_run = self._calculate_next_run(
                schedule_data.frequency,
                schedule_data.time,
                schedule_data.day_of_week,
                schedule_data.day_of_month,
                schedule_data.timezone,
            )

        schedule_doc = {
            "project_id": schedule_data.project_id,
            "user_id": user_id,
            "enabled": schedule_data.enabled,
            "frequency": schedule_data.frequency,
            "time": schedule_data.time,
            "day_of_week": schedule_data.day_of_week,
            "day_of_month": schedule_data.day_of_month,
            "timezone": schedule_data.timezone,
            "max_retries": schedule_data.max_retries,
            "notify_on_failure": schedule_data.notify_on_failure,
            "next_run": next_run,
            "last_run": None,
            "last_status": None,
            "consecutive_failures": 0,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(schedule_doc)
        schedule_doc["id"] = str(result.inserted_id)

        return Schedule(**schedule_doc)

    async def get_schedule(self, project_id: str, user_id: str) -> Schedule:
        """Get schedule for a project."""
        doc = await self.collection.find_one(
            {"project_id": project_id, "user_id": user_id}
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )
        return self._doc_to_model(doc, Schedule)

    async def get_schedule_by_id(self, schedule_id: str, user_id: str) -> Schedule:
        """Get schedule by ID."""
        doc = await self.collection.find_one(
            {"_id": ObjectId(schedule_id), "user_id": user_id}
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )
        return self._doc_to_model(doc, Schedule)

    async def get_schedules(self, user_id: str) -> ScheduleList:
        """Get all schedules for a user."""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        schedules = await cursor.to_list(length=None)

        return ScheduleList(
            items=[self._doc_to_model(s, Schedule) for s in schedules],
            total=len(schedules),
        )

    async def update_schedule(
        self,
        project_id: str,
        user_id: str,
        update_data: ScheduleUpdate,
    ) -> Schedule:
        """Update a schedule."""
        schedule = await self.get_schedule(project_id, user_id)

        update_dict = update_data.model_dump(exclude_none=True)
        if not update_dict:
            return schedule

        update_dict["updated_at"] = datetime.now(timezone.utc)

        # Recalculate next run if relevant fields changed
        if any(k in update_dict for k in ["enabled", "frequency", "time", "day_of_week", "day_of_month", "timezone"]):
            # Merge with existing values
            frequency = update_dict.get("frequency", schedule.frequency)
            time = update_dict.get("time", schedule.time)
            day_of_week = update_dict.get("day_of_week", schedule.day_of_week)
            day_of_month = update_dict.get("day_of_month", schedule.day_of_month)
            tz = update_dict.get("timezone", schedule.timezone)
            enabled = update_dict.get("enabled", schedule.enabled)

            if enabled:
                update_dict["next_run"] = self._calculate_next_run(
                    frequency, time, day_of_week, day_of_month, tz
                )
            else:
                update_dict["next_run"] = None

        result = await self.collection.find_one_and_update(
            {"project_id": project_id, "user_id": user_id},
            {"$set": update_dict},
            return_document=True,
        )

        return self._doc_to_model(result, Schedule)

    async def delete_schedule(self, project_id: str, user_id: str) -> None:
        """Delete a schedule."""
        result = await self.collection.delete_one(
            {"project_id": project_id, "user_id": user_id}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )

    async def get_due_schedules(self, limit: int = 100) -> list[Schedule]:
        """Get schedules that are due to run."""
        now = datetime.now(timezone.utc)

        cursor = self.collection.find(
            {
                "enabled": True,
                "next_run": {"$lte": now},
            }
        ).limit(limit)

        schedules = await cursor.to_list(length=limit)
        return [self._doc_to_model(s, Schedule) for s in schedules]

    async def record_execution(
        self,
        schedule_id: str,
        job_id: str | None,
        status: str,
        results_count: int = 0,
        error: str | None = None,
    ) -> None:
        """Record a schedule execution."""
        now = datetime.now(timezone.utc)

        # Create execution record
        execution_doc = {
            "schedule_id": schedule_id,
            "job_id": job_id,
            "status": status,
            "started_at": now,
            "completed_at": now if status in ("completed", "failed", "skipped") else None,
            "results_count": results_count,
            "error": error,
            "retry_count": 0,
        }
        await self.executions_collection.insert_one(execution_doc)

        # Update schedule
        schedule = await self.collection.find_one({"_id": ObjectId(schedule_id)})
        if schedule:
            update = {
                "last_run": now,
                "last_status": status,
                "updated_at": now,
            }

            if status == "completed":
                update["consecutive_failures"] = 0
                # Calculate next run
                update["next_run"] = self._calculate_next_run(
                    schedule["frequency"],
                    schedule.get("time"),
                    schedule.get("day_of_week"),
                    schedule.get("day_of_month"),
                    schedule.get("timezone", "UTC"),
                )
            elif status == "failed":
                update["consecutive_failures"] = schedule.get("consecutive_failures", 0) + 1
                # Disable if too many failures
                if update["consecutive_failures"] >= schedule.get("max_retries", 3):
                    update["enabled"] = False
                    update["next_run"] = None
                else:
                    # Retry in 5 minutes
                    update["next_run"] = now + timedelta(minutes=5)

            await self.collection.update_one(
                {"_id": ObjectId(schedule_id)},
                {"$set": update},
            )

    async def get_executions(
        self,
        schedule_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> ScheduleExecutionList:
        """Get execution history for a schedule."""
        query = {"schedule_id": schedule_id}
        total = await self.executions_collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            self.executions_collection.find(query)
            .sort("started_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        executions = await cursor.to_list(length=page_size)

        return ScheduleExecutionList(
            items=[ScheduleExecution(**e) for e in executions],
            total=total,
            page=page,
            page_size=page_size,
        )


def get_schedule_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ScheduleRepository:
    """Dependency for getting schedule repository."""
    return ScheduleRepository(db)
