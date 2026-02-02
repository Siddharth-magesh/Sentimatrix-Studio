"""Webhook endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.database import get_database
from app.core.deps import get_current_user
from app.models.user import User
from app.models.webhook import (
    Webhook,
    WebhookCreate,
    WebhookDeliveryList,
    WebhookList,
    WebhookTestResult,
    WebhookUpdate,
)
from app.repositories.webhook import WebhookRepository, get_webhook_repository
from app.services.webhook_service import WebhookService

router = APIRouter()


@router.get(
    "",
    response_model=WebhookList,
    summary="List webhooks",
)
async def list_webhooks(
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
    project_id: str | None = Query(None, description="Filter by project"),
) -> WebhookList:
    """
    Get all webhooks for the current user.

    Optionally filter by project to see only webhooks that will be triggered
    for that project (including global webhooks).
    """
    return await webhook_repo.get_webhooks(current_user.id, project_id)


@router.post(
    "",
    response_model=Webhook,
    status_code=status.HTTP_201_CREATED,
    summary="Create webhook",
)
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
    project_id: str | None = Query(None, description="Project to attach webhook to (null for global)"),
) -> Webhook:
    """
    Create a new webhook.

    - **url**: Webhook URL to receive events (required)
    - **events**: List of events to trigger on
    - **secret**: Optional secret for payload signing
    - **headers**: Custom headers to include in requests

    Available events:
    - job.started, job.completed, job.failed
    - analysis.completed
    - schedule.triggered, schedule.failed
    - target.added, target.error
    """
    return await webhook_repo.create_webhook(
        user_id=current_user.id,
        webhook_data=webhook_data,
        project_id=project_id,
    )


@router.get(
    "/{webhook_id}",
    response_model=Webhook,
    summary="Get webhook",
)
async def get_webhook(
    webhook_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
) -> Webhook:
    """
    Get a specific webhook by ID.
    """
    return await webhook_repo.get_webhook(webhook_id, current_user.id)


@router.put(
    "/{webhook_id}",
    response_model=Webhook,
    summary="Update webhook",
)
async def update_webhook(
    webhook_id: str,
    update_data: WebhookUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
) -> Webhook:
    """
    Update a webhook.

    Only provided fields will be updated.
    """
    return await webhook_repo.update_webhook(
        webhook_id=webhook_id,
        user_id=current_user.id,
        update_data=update_data,
    )


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete webhook",
)
async def delete_webhook(
    webhook_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
) -> None:
    """
    Delete a webhook.
    """
    await webhook_repo.delete_webhook(webhook_id, current_user.id)


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResult,
    summary="Test webhook",
)
async def test_webhook(
    webhook_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
    db=Depends(get_database),
) -> WebhookTestResult:
    """
    Test a webhook by sending a test payload.

    This will send a test event to the webhook URL and return the result.
    """
    webhook = await webhook_repo.get_webhook(webhook_id, current_user.id)

    service = WebhookService(db)
    return await service.test_webhook(webhook)


@router.get(
    "/{webhook_id}/deliveries",
    response_model=WebhookDeliveryList,
    summary="Get webhook deliveries",
)
async def get_webhook_deliveries(
    webhook_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> WebhookDeliveryList:
    """
    Get delivery history for a webhook.

    Shows recent delivery attempts with status codes, response times, and errors.
    """
    # Verify ownership
    await webhook_repo.get_webhook(webhook_id, current_user.id)

    return await webhook_repo.get_deliveries(
        webhook_id=webhook_id,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/{webhook_id}/toggle",
    response_model=Webhook,
    summary="Toggle webhook",
)
async def toggle_webhook(
    webhook_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    webhook_repo: Annotated[WebhookRepository, Depends(get_webhook_repository)],
) -> Webhook:
    """
    Toggle a webhook on/off.
    """
    webhook = await webhook_repo.get_webhook(webhook_id, current_user.id)

    return await webhook_repo.update_webhook(
        webhook_id=webhook_id,
        user_id=current_user.id,
        update_data=WebhookUpdate(enabled=not webhook.enabled),
    )


@router.get(
    "/events/available",
    response_model=list[dict],
    summary="List available events",
)
async def list_available_events(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    """
    Get list of available webhook events and their descriptions.
    """
    return [
        {"event": "job.started", "description": "Triggered when a scrape job starts"},
        {"event": "job.completed", "description": "Triggered when a scrape job completes successfully"},
        {"event": "job.failed", "description": "Triggered when a scrape job fails"},
        {"event": "analysis.completed", "description": "Triggered when analysis completes for results"},
        {"event": "schedule.triggered", "description": "Triggered when a scheduled job runs"},
        {"event": "schedule.failed", "description": "Triggered when a scheduled job fails"},
        {"event": "target.added", "description": "Triggered when a new target is added"},
        {"event": "target.error", "description": "Triggered when a target encounters an error"},
    ]
