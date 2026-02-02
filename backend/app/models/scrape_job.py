"""Scrape job model definitions."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class TargetJobStatus(StudioBaseModel):
    """Status of a single target in a scrape job."""

    target_id: str
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    progress: int = 0
    results_count: int = 0
    error: str | None = None


class ScrapeJobOptions(StudioBaseModel):
    """Scrape job options."""

    max_results: int = Field(default=100, ge=1, le=1000)
    include_replies: bool = False
    date_from: datetime | None = None
    date_to: datetime | None = None


class ScrapeJobStats(StudioBaseModel):
    """Scrape job statistics."""

    targets_total: int = 0
    targets_completed: int = 0
    results_total: int = 0
    requests_made: int = 0
    errors_count: int = 0


class ScrapeJobCreate(StudioBaseModel):
    """Model for creating a scrape job."""

    target_ids: list[str] | None = None  # None means all targets
    options: ScrapeJobOptions = Field(default_factory=ScrapeJobOptions)


class ScrapeJob(MongoBaseModel, TimestampMixin):
    """Scrape job model for API responses."""

    project_id: str
    user_id: str
    status: Literal["queued", "running", "completed", "failed", "cancelled"] = "queued"
    progress: int = Field(default=0, ge=0, le=100)
    targets: list[TargetJobStatus] = Field(default_factory=list)
    options: ScrapeJobOptions = Field(default_factory=ScrapeJobOptions)
    stats: ScrapeJobStats = Field(default_factory=ScrapeJobStats)
    trigger: Literal["manual", "scheduled", "api"] = "manual"
    triggered_by: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


class ScrapeJobInDB(ScrapeJob):
    """Scrape job model with all database fields."""

    pass


class ScrapeJobList(StudioBaseModel):
    """Paginated scrape job list response."""

    items: list[ScrapeJob]
    total: int
    page: int
    page_size: int
