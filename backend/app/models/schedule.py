"""Schedule model definitions."""

from datetime import datetime, time
from typing import Any, Literal

from pydantic import Field, field_validator

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class ScheduleCreate(StudioBaseModel):
    """Model for creating a schedule."""

    project_id: str
    enabled: bool = True
    frequency: Literal["hourly", "daily", "weekly", "monthly"] = "daily"
    time: str | None = Field(default="09:00", description="Time in HH:MM format (for daily+)")
    day_of_week: int | None = Field(default=None, ge=0, le=6, description="Day of week (0=Monday, for weekly)")
    day_of_month: int | None = Field(default=None, ge=1, le=28, description="Day of month (for monthly)")
    timezone: str = Field(default="UTC")
    max_retries: int = Field(default=3, ge=0, le=10)
    notify_on_failure: bool = True

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str | None) -> str | None:
        """Validate time format."""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v


class ScheduleUpdate(StudioBaseModel):
    """Model for updating a schedule."""

    enabled: bool | None = None
    frequency: Literal["hourly", "daily", "weekly", "monthly"] | None = None
    time: str | None = None
    day_of_week: int | None = None
    day_of_month: int | None = None
    timezone: str | None = None
    max_retries: int | None = None
    notify_on_failure: bool | None = None


class ScheduleExecution(StudioBaseModel):
    """Record of a schedule execution."""

    schedule_id: str
    job_id: str | None = None
    status: Literal["pending", "running", "completed", "failed", "skipped"] = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    results_count: int = 0
    error: str | None = None
    retry_count: int = 0


class Schedule(MongoBaseModel, TimestampMixin):
    """Schedule model for API responses."""

    project_id: str
    user_id: str
    enabled: bool = True
    frequency: Literal["hourly", "daily", "weekly", "monthly"] = "daily"
    time: str | None = "09:00"
    day_of_week: int | None = None
    day_of_month: int | None = None
    timezone: str = "UTC"
    max_retries: int = 3
    notify_on_failure: bool = True
    next_run: datetime | None = None
    last_run: datetime | None = None
    last_status: Literal["pending", "completed", "failed"] | None = None
    consecutive_failures: int = 0


class ScheduleInDB(Schedule):
    """Schedule model with all database fields."""

    pass


class ScheduleList(StudioBaseModel):
    """Paginated schedule list response."""

    items: list[Schedule]
    total: int


class ScheduleExecutionList(StudioBaseModel):
    """Paginated schedule execution list."""

    items: list[ScheduleExecution]
    total: int
    page: int
    page_size: int
