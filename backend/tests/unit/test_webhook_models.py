"""Tests for webhook models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.webhook import (
    Webhook,
    WebhookCreate,
    WebhookUpdate,
    WebhookDelivery,
    WebhookTestResult,
)


class TestWebhookModels:
    """Test webhook models."""

    def test_webhook_create_defaults(self):
        """Test webhook creation with defaults."""
        webhook = WebhookCreate(url="https://example.com/webhook")

        assert webhook.url == "https://example.com/webhook"
        assert webhook.events == ["job.completed"]
        assert webhook.enabled is True
        assert webhook.secret is None
        assert webhook.headers == {}

    def test_webhook_create_custom(self):
        """Test webhook creation with custom values."""
        webhook = WebhookCreate(
            url="https://example.com/webhook",
            events=["job.started", "job.completed", "job.failed"],
            secret="my-secret-key",
            headers={"X-Custom-Header": "value"},
        )

        assert len(webhook.events) == 3
        assert webhook.secret == "my-secret-key"
        assert "X-Custom-Header" in webhook.headers

    def test_webhook_create_invalid_url(self):
        """Test invalid URL format."""
        with pytest.raises(ValidationError) as exc_info:
            WebhookCreate(url="not-a-url")

        assert "URL must start with http:// or https://" in str(exc_info.value)

    def test_webhook_create_invalid_event(self):
        """Test invalid event type."""
        with pytest.raises(ValidationError) as exc_info:
            WebhookCreate(
                url="https://example.com/webhook",
                events=["invalid.event"],
            )

        assert "Invalid event" in str(exc_info.value)

    def test_webhook_create_http_url(self):
        """Test HTTP URL is valid."""
        webhook = WebhookCreate(url="http://localhost:8080/webhook")

        assert webhook.url == "http://localhost:8080/webhook"

    def test_all_valid_events(self):
        """Test all valid events can be used."""
        valid_events = [
            "job.started",
            "job.completed",
            "job.failed",
            "analysis.completed",
            "schedule.triggered",
            "schedule.failed",
            "target.added",
            "target.error",
        ]

        webhook = WebhookCreate(
            url="https://example.com/webhook",
            events=valid_events,
        )

        assert len(webhook.events) == len(valid_events)


class TestWebhookUpdate:
    """Test webhook update model."""

    def test_update_partial(self):
        """Test partial update."""
        update = WebhookUpdate(enabled=False)

        assert update.enabled is False
        assert update.url is None
        assert update.events is None

    def test_update_url(self):
        """Test updating URL."""
        update = WebhookUpdate(url="https://new-url.com/webhook")

        assert update.url == "https://new-url.com/webhook"

    def test_update_multiple_fields(self):
        """Test updating multiple fields."""
        update = WebhookUpdate(
            events=["job.started"],
            secret="new-secret",
            enabled=True,
        )

        assert update.events == ["job.started"]
        assert update.secret == "new-secret"


class TestWebhookDelivery:
    """Test webhook delivery model."""

    def test_delivery_success(self):
        """Test successful delivery."""
        delivery = WebhookDelivery(
            webhook_id="webhook123",
            event="job.completed",
            payload={"job_id": "job456"},
            status_code=200,
            response_body="OK",
            delivered_at=datetime.now(),
            duration_ms=150.5,
        )

        assert delivery.status_code == 200
        assert delivery.error is None
        assert delivery.duration_ms == 150.5

    def test_delivery_failure(self):
        """Test failed delivery."""
        delivery = WebhookDelivery(
            webhook_id="webhook123",
            event="job.completed",
            payload={},
            status_code=500,
            error="Internal Server Error",
            delivered_at=datetime.now(),
        )

        assert delivery.status_code == 500
        assert delivery.error == "Internal Server Error"

    def test_delivery_timeout(self):
        """Test timeout delivery."""
        delivery = WebhookDelivery(
            webhook_id="webhook123",
            event="job.completed",
            payload={},
            error="Request timed out",
            delivered_at=datetime.now(),
        )

        assert delivery.status_code is None
        assert delivery.error == "Request timed out"


class TestWebhookTestResult:
    """Test webhook test result model."""

    def test_successful_test(self):
        """Test successful webhook test."""
        result = WebhookTestResult(
            success=True,
            status_code=200,
            response_time_ms=85.3,
        )

        assert result.success is True
        assert result.status_code == 200
        assert result.error is None

    def test_failed_test(self):
        """Test failed webhook test."""
        result = WebhookTestResult(
            success=False,
            status_code=404,
            error="Not Found",
        )

        assert result.success is False
        assert result.error == "Not Found"

    def test_connection_error(self):
        """Test connection error."""
        result = WebhookTestResult(
            success=False,
            error="Connection refused",
        )

        assert result.success is False
        assert result.status_code is None
