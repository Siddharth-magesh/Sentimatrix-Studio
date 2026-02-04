"""Webhook repository for database operations."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.webhook import (
    Webhook,
    WebhookCreate,
    WebhookDelivery,
    WebhookDeliveryList,
    WebhookList,
    WebhookUpdate,
)
from app.repositories.base import BaseRepository


class WebhookRepository(BaseRepository):
    """Repository for webhook database operations."""

    collection_name = "webhooks"
    model_class = Webhook

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__()
        self.deliveries_collection = db["webhook_deliveries"]

    async def create_webhook(
        self,
        user_id: str,
        webhook_data: WebhookCreate,
        project_id: str | None = None,
    ) -> Webhook:
        """Create a new webhook."""
        now = datetime.now(timezone.utc)

        webhook_doc = {
            "user_id": user_id,
            "project_id": project_id,
            "url": webhook_data.url,
            "events": webhook_data.events,
            "secret": webhook_data.secret,
            "enabled": webhook_data.enabled,
            "headers": webhook_data.headers,
            "last_triggered": None,
            "last_status": None,
            "consecutive_failures": 0,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(webhook_doc)
        webhook_doc["id"] = str(result.inserted_id)

        return Webhook(**webhook_doc)

    async def get_webhook(self, webhook_id: str, user_id: str) -> Webhook:
        """Get a webhook by ID."""
        doc = await self.collection.find_one(
            {"_id": ObjectId(webhook_id), "user_id": user_id}
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )
        return self._doc_to_model(doc, Webhook)

    async def get_webhooks(
        self,
        user_id: str,
        project_id: str | None = None,
    ) -> WebhookList:
        """Get all webhooks for a user, optionally filtered by project."""
        query: dict[str, Any] = {"user_id": user_id}
        if project_id:
            query["$or"] = [
                {"project_id": project_id},
                {"project_id": None},  # Global webhooks
            ]

        cursor = self.collection.find(query).sort("created_at", -1)
        webhooks = await cursor.to_list(length=None)

        return WebhookList(
            items=[self._doc_to_model(w, Webhook) for w in webhooks],
            total=len(webhooks),
        )

    async def get_webhooks_for_event(
        self,
        user_id: str,
        event: str,
        project_id: str | None = None,
    ) -> list[Webhook]:
        """Get enabled webhooks that are subscribed to an event."""
        query: dict[str, Any] = {
            "user_id": user_id,
            "enabled": True,
            "events": event,
        }

        if project_id:
            query["$or"] = [
                {"project_id": project_id},
                {"project_id": None},
            ]
        else:
            query["project_id"] = None

        cursor = self.collection.find(query)
        webhooks = await cursor.to_list(length=None)

        return [self._doc_to_model(w, Webhook) for w in webhooks]

    async def update_webhook(
        self,
        webhook_id: str,
        user_id: str,
        update_data: WebhookUpdate,
    ) -> Webhook:
        """Update a webhook."""
        update_dict = update_data.model_dump(exclude_none=True)
        if not update_dict:
            return await self.get_webhook(webhook_id, user_id)

        update_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(webhook_id), "user_id": user_id},
            {"$set": update_dict},
            return_document=True,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )

        return self._doc_to_model(result, Webhook)

    async def delete_webhook(self, webhook_id: str, user_id: str) -> None:
        """Delete a webhook."""
        result = await self.collection.delete_one(
            {"_id": ObjectId(webhook_id), "user_id": user_id}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found",
            )

    async def record_delivery(
        self,
        webhook_id: str,
        event: str,
        payload: dict[str, Any],
        status_code: int | None,
        response_body: str | None,
        error: str | None,
        duration_ms: float | None,
    ) -> None:
        """Record a webhook delivery attempt."""
        now = datetime.now(timezone.utc)

        delivery_doc = {
            "webhook_id": webhook_id,
            "event": event,
            "payload": payload,
            "status_code": status_code,
            "response_body": response_body[:1000] if response_body else None,  # Truncate
            "error": error,
            "delivered_at": now,
            "duration_ms": duration_ms,
        }
        await self.deliveries_collection.insert_one(delivery_doc)

        # Update webhook status
        success = status_code is not None and 200 <= status_code < 300
        update: dict[str, Any] = {
            "last_triggered": now,
            "last_status": status_code,
            "updated_at": now,
        }

        if success:
            update["consecutive_failures"] = 0
        else:
            update["$inc"] = {"consecutive_failures": 1}
            # Disable after 5 consecutive failures
            webhook = await self.collection.find_one({"_id": ObjectId(webhook_id)})
            if webhook and webhook.get("consecutive_failures", 0) >= 4:
                update["enabled"] = False

        if "$inc" in update:
            inc_update = update.pop("$inc")
            await self.collection.update_one(
                {"_id": ObjectId(webhook_id)},
                {"$set": update, "$inc": inc_update},
            )
        else:
            await self.collection.update_one(
                {"_id": ObjectId(webhook_id)},
                {"$set": update},
            )

    async def get_deliveries(
        self,
        webhook_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> WebhookDeliveryList:
        """Get delivery history for a webhook."""
        query = {"webhook_id": webhook_id}
        total = await self.deliveries_collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            self.deliveries_collection.find(query)
            .sort("delivered_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        deliveries = await cursor.to_list(length=page_size)

        items = []
        for d in deliveries:
            d["id"] = str(d.pop("_id"))
            items.append(WebhookDelivery(**d))

        return WebhookDeliveryList(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )


def get_webhook_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> WebhookRepository:
    """Dependency for getting webhook repository."""
    return WebhookRepository(db)
