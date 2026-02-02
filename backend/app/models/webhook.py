"""Webhook model definitions."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, HttpUrl, field_validator

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class WebhookCreate(StudioBaseModel):
    """Model for creating a webhook."""

    url: str
    events: list[str] = Field(
        default_factory=lambda: ["job.completed"],
        description="Events to trigger webhook",
    )
    secret: str | None = Field(default=None, description="Secret for signing payloads")
    enabled: bool = True
    headers: dict[str, str] = Field(default_factory=dict)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        """Validate event types."""
        valid_events = {
            "job.started",
            "job.completed",
            "job.failed",
            "analysis.completed",
            "schedule.triggered",
            "schedule.failed",
            "target.added",
            "target.error",
        }
        for event in v:
            if event not in valid_events:
                raise ValueError(f"Invalid event: {event}. Valid events: {valid_events}")
        return v


class WebhookUpdate(StudioBaseModel):
    """Model for updating a webhook."""

    url: str | None = None
    events: list[str] | None = None
    secret: str | None = None
    enabled: bool | None = None
    headers: dict[str, str] | None = None


class Webhook(MongoBaseModel, TimestampMixin):
    """Webhook model for API responses."""

    user_id: str
    project_id: str | None = None  # None means all projects
    url: str
    events: list[str]
    secret: str | None = None
    enabled: bool = True
    headers: dict[str, str] = Field(default_factory=dict)
    last_triggered: datetime | None = None
    last_status: int | None = None
    consecutive_failures: int = 0


class WebhookInDB(Webhook):
    """Webhook model with all database fields."""

    pass


class WebhookDelivery(StudioBaseModel):
    """Record of a webhook delivery attempt."""

    id: str | None = None
    webhook_id: str
    event: str
    payload: dict[str, Any]
    status_code: int | None = None
    response_body: str | None = None
    error: str | None = None
    delivered_at: datetime
    duration_ms: float | None = None


class WebhookList(StudioBaseModel):
    """List of webhooks."""

    items: list[Webhook]
    total: int


class WebhookDeliveryList(StudioBaseModel):
    """Paginated webhook delivery list."""

    items: list[WebhookDelivery]
    total: int
    page: int
    page_size: int


class WebhookTestResult(StudioBaseModel):
    """Result of testing a webhook."""

    success: bool
    status_code: int | None = None
    response_time_ms: float | None = None
    error: str | None = None
