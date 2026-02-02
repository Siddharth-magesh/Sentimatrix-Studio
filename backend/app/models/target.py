"""Target model definitions."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, HttpUrl, field_validator

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class PlatformData(StudioBaseModel):
    """Platform-specific parsed data."""

    asin: str | None = None  # Amazon
    app_id: int | None = None  # Steam
    video_id: str | None = None  # YouTube
    post_id: str | None = None  # Reddit
    place_id: str | None = None  # Google


class TargetOptions(StudioBaseModel):
    """Platform-specific target options."""

    country: str | None = None
    language: str | None = None
    sort_by: str | None = None
    filter: dict[str, Any] | None = None


class TargetStats(StudioBaseModel):
    """Target statistics."""

    results_count: int = 0
    last_scraped_at: datetime | None = None
    last_result_date: datetime | None = None


class TargetBase(StudioBaseModel):
    """Base target model."""

    url: str
    label: str | None = Field(default=None, max_length=100)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class TargetCreate(TargetBase):
    """Model for creating a target."""

    options: TargetOptions | None = None
    metadata: dict[str, Any] | None = None


class TargetBulkCreate(StudioBaseModel):
    """Model for bulk creating targets."""

    urls: list[str]
    options: TargetOptions | None = None

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        if len(v) > 50:
            raise ValueError("Maximum 50 URLs per request")
        for url in v:
            if not url.startswith(("http://", "https://")):
                raise ValueError(f"Invalid URL: {url}")
        return v


class TargetUpdate(StudioBaseModel):
    """Model for updating a target."""

    label: str | None = Field(default=None, max_length=100)
    status: Literal["active", "paused"] | None = None
    options: TargetOptions | None = None
    metadata: dict[str, Any] | None = None


class Target(TargetBase, MongoBaseModel, TimestampMixin):
    """Target model for API responses."""

    project_id: str
    user_id: str
    platform: str | None = None
    detected_type: str | None = None
    platform_data: PlatformData = Field(default_factory=PlatformData)
    options: TargetOptions = Field(default_factory=TargetOptions)
    metadata: dict[str, Any] = Field(default_factory=dict)
    stats: TargetStats = Field(default_factory=TargetStats)
    status: Literal["active", "paused", "error"] = "active"
    error_message: str | None = None


class TargetInDB(Target):
    """Target model with all database fields."""

    pass


class TargetList(StudioBaseModel):
    """Paginated target list response."""

    items: list[Target]
    total: int
