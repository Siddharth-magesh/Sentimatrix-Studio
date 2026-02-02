"""Webhook delivery service."""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.webhook import Webhook, WebhookTestResult
from app.repositories.webhook import WebhookRepository

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for delivering webhooks."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.webhook_repo = WebhookRepository(db)
        self._timeout = 30.0  # 30 second timeout
        self._retry_delays = [60, 300, 1800]  # 1min, 5min, 30min

    def _sign_payload(self, payload: str, secret: str) -> str:
        """Create HMAC-SHA256 signature for payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    async def deliver_webhook(
        self,
        webhook: Webhook,
        event: str,
        payload: dict[str, Any],
    ) -> bool:
        """
        Deliver a webhook payload.

        Returns True if delivery was successful.
        """
        # Build full payload
        full_payload = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }
        payload_json = json.dumps(full_payload, default=str)

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SentimatrixStudio/1.0",
            "X-Webhook-Event": event,
            **webhook.headers,
        }

        # Add signature if secret is configured
        if webhook.secret:
            signature = self._sign_payload(payload_json, webhook.secret)
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        # Deliver
        start_time = time.time()
        status_code = None
        response_body = None
        error = None

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers,
                )
                status_code = response.status_code
                response_body = response.text

        except httpx.TimeoutException:
            error = "Request timed out"
            logger.warning(f"Webhook delivery timed out: {webhook.url}")
        except httpx.RequestError as e:
            error = str(e)
            logger.warning(f"Webhook delivery error: {webhook.url} - {e}")
        except Exception as e:
            error = str(e)
            logger.error(f"Unexpected webhook error: {webhook.url} - {e}")

        duration_ms = (time.time() - start_time) * 1000

        # Record delivery
        await self.webhook_repo.record_delivery(
            webhook_id=webhook.id,
            event=event,
            payload=full_payload,
            status_code=status_code,
            response_body=response_body,
            error=error,
            duration_ms=duration_ms,
        )

        success = status_code is not None and 200 <= status_code < 300
        if success:
            logger.info(f"Webhook delivered: {webhook.url} ({status_code})")
        else:
            logger.warning(f"Webhook delivery failed: {webhook.url} ({status_code or error})")

        return success

    async def trigger_event(
        self,
        user_id: str,
        event: str,
        payload: dict[str, Any],
        project_id: str | None = None,
    ) -> int:
        """
        Trigger webhooks for an event.

        Returns the number of webhooks triggered.
        """
        webhooks = await self.webhook_repo.get_webhooks_for_event(
            user_id=user_id,
            event=event,
            project_id=project_id,
        )

        if not webhooks:
            return 0

        # Deliver to all webhooks in parallel
        tasks = [
            self.deliver_webhook(webhook, event, payload)
            for webhook in webhooks
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        return len(webhooks)

    async def test_webhook(self, webhook: Webhook) -> WebhookTestResult:
        """Test a webhook endpoint with a test payload."""
        test_payload = {
            "test": True,
            "message": "This is a test webhook delivery from Sentimatrix Studio",
        }

        start_time = time.time()
        status_code = None
        error = None

        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "SentimatrixStudio/1.0",
                "X-Webhook-Event": "test",
                **webhook.headers,
            }

            payload_json = json.dumps({
                "event": "test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": test_payload,
            })

            if webhook.secret:
                signature = self._sign_payload(payload_json, webhook.secret)
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers,
                )
                status_code = response.status_code

        except httpx.TimeoutException:
            error = "Request timed out"
        except httpx.RequestError as e:
            error = str(e)
        except Exception as e:
            error = str(e)

        duration_ms = (time.time() - start_time) * 1000
        success = status_code is not None and 200 <= status_code < 300

        return WebhookTestResult(
            success=success,
            status_code=status_code,
            response_time_ms=duration_ms,
            error=error,
        )


# Event helper functions
async def trigger_job_started(
    db: AsyncIOMotorDatabase,
    user_id: str,
    project_id: str,
    job_id: str,
    targets_count: int,
) -> None:
    """Trigger job.started event."""
    service = WebhookService(db)
    await service.trigger_event(
        user_id=user_id,
        event="job.started",
        payload={
            "job_id": job_id,
            "project_id": project_id,
            "targets_count": targets_count,
        },
        project_id=project_id,
    )


async def trigger_job_completed(
    db: AsyncIOMotorDatabase,
    user_id: str,
    project_id: str,
    job_id: str,
    results_count: int,
    duration_seconds: float,
) -> None:
    """Trigger job.completed event."""
    service = WebhookService(db)
    await service.trigger_event(
        user_id=user_id,
        event="job.completed",
        payload={
            "job_id": job_id,
            "project_id": project_id,
            "results_count": results_count,
            "duration_seconds": duration_seconds,
        },
        project_id=project_id,
    )


async def trigger_job_failed(
    db: AsyncIOMotorDatabase,
    user_id: str,
    project_id: str,
    job_id: str,
    error: str,
) -> None:
    """Trigger job.failed event."""
    service = WebhookService(db)
    await service.trigger_event(
        user_id=user_id,
        event="job.failed",
        payload={
            "job_id": job_id,
            "project_id": project_id,
            "error": error,
        },
        project_id=project_id,
    )
