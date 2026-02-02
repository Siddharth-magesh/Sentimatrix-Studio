"""API key repository for database operations."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.encryption import encrypt_api_key, decrypt_api_key, mask_api_key
from app.models.llm_provider import (
    APIKey,
    APIKeyCreate,
    APIKeyResponse,
    LLM_PROVIDERS,
)
from app.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository):
    """Repository for API key database operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "api_keys")

    async def create_api_key(
        self,
        user_id: str,
        key_data: APIKeyCreate,
    ) -> APIKeyResponse:
        """Create or update an API key for a provider."""
        now = datetime.now(timezone.utc)

        # Check if key already exists for this provider
        existing = await self.collection.find_one(
            {"user_id": user_id, "provider": key_data.provider}
        )

        # Encrypt the API key
        encrypted_key = encrypt_api_key(key_data.api_key)

        if existing:
            # Update existing key
            await self.collection.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "encrypted_key": encrypted_key,
                        "label": key_data.label,
                        "is_valid": None,  # Reset validation
                        "updated_at": now,
                    }
                },
            )
            key_id = str(existing["_id"])
        else:
            # Create new key
            key_doc = {
                "user_id": user_id,
                "provider": key_data.provider,
                "encrypted_key": encrypted_key,
                "label": key_data.label,
                "is_valid": None,
                "last_used": None,
                "last_validated": None,
                "created_at": now,
                "updated_at": now,
            }
            result = await self.collection.insert_one(key_doc)
            key_id = str(result.inserted_id)

        return APIKeyResponse(
            id=key_id,
            provider=key_data.provider,
            label=key_data.label,
            masked_key=mask_api_key(key_data.api_key),
            is_valid=None,
            last_used=None,
            created_at=now,
        )

    async def get_api_key(self, user_id: str, provider: str) -> str | None:
        """Get decrypted API key for a provider."""
        doc = await self.collection.find_one(
            {"user_id": user_id, "provider": provider}
        )
        if not doc:
            return None

        # Update last used
        await self.collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"last_used": datetime.now(timezone.utc)}},
        )

        return decrypt_api_key(doc["encrypted_key"])

    async def get_api_keys(self, user_id: str) -> list[APIKeyResponse]:
        """Get all API keys for a user (masked)."""
        cursor = self.collection.find({"user_id": user_id})
        keys = await cursor.to_list(length=None)

        responses = []
        for doc in keys:
            # Decrypt to get masked version
            decrypted = decrypt_api_key(doc["encrypted_key"])
            responses.append(
                APIKeyResponse(
                    id=str(doc["_id"]),
                    provider=doc["provider"],
                    label=doc.get("label"),
                    masked_key=mask_api_key(decrypted),
                    is_valid=doc.get("is_valid"),
                    last_used=doc.get("last_used"),
                    created_at=doc["created_at"],
                )
            )

        return responses

    async def delete_api_key(self, user_id: str, provider: str) -> None:
        """Delete an API key for a provider."""
        result = await self.collection.delete_one(
            {"user_id": user_id, "provider": provider}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key for {provider} not found",
            )

    async def update_validation_status(
        self,
        user_id: str,
        provider: str,
        is_valid: bool,
    ) -> None:
        """Update the validation status of an API key."""
        await self.collection.update_one(
            {"user_id": user_id, "provider": provider},
            {
                "$set": {
                    "is_valid": is_valid,
                    "last_validated": datetime.now(timezone.utc),
                }
            },
        )

    async def has_api_key(self, user_id: str, provider: str) -> bool:
        """Check if user has an API key for a provider."""
        count = await self.collection.count_documents(
            {"user_id": user_id, "provider": provider}
        )
        return count > 0

    async def get_configured_providers(self, user_id: str) -> list[str]:
        """Get list of providers that user has configured."""
        cursor = self.collection.find(
            {"user_id": user_id},
            {"provider": 1},
        )
        keys = await cursor.to_list(length=None)
        return [k["provider"] for k in keys]


def get_api_key_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> APIKeyRepository:
    """Dependency for getting API key repository."""
    return APIKeyRepository(db)
