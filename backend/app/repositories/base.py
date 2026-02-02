"""Base repository with common CRUD operations."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.db.mongodb import MongoDB

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository with common database operations."""

    collection_name: str
    model_class: type[T]

    def __init__(self) -> None:
        self._collection: AsyncIOMotorCollection | None = None

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection."""
        if self._collection is None:
            self._collection = MongoDB.get_collection(self.collection_name)
        return self._collection

    async def create(self, data: dict[str, Any]) -> T:
        """Create a new document."""
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(data)
        data["_id"] = result.inserted_id

        return self.model_class(**data)

    async def get_by_id(self, id: str) -> T | None:
        """Get a document by ID."""
        if not ObjectId.is_valid(id):
            return None

        doc = await self.collection.find_one({"_id": ObjectId(id)})
        if doc:
            return self.model_class(**doc)
        return None

    async def get_one(self, filter: dict[str, Any]) -> T | None:
        """Get a single document matching the filter."""
        doc = await self.collection.find_one(filter)
        if doc:
            return self.model_class(**doc)
        return None

    async def get_many(
        self,
        filter: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 100,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[T]:
        """Get multiple documents matching the filter."""
        filter = filter or {}
        cursor = self.collection.find(filter).skip(skip).limit(limit)

        if sort:
            cursor = cursor.sort(sort)

        docs = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in docs]

    async def update(self, id: str, data: dict[str, Any]) -> T | None:
        """Update a document by ID."""
        if not ObjectId.is_valid(id):
            return None

        data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": data},
            return_document=True,
        )

        if result:
            return self.model_class(**result)
        return None

    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        if not ObjectId.is_valid(id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def count(self, filter: dict[str, Any] | None = None) -> int:
        """Count documents matching the filter."""
        filter = filter or {}
        return await self.collection.count_documents(filter)

    async def exists(self, filter: dict[str, Any]) -> bool:
        """Check if a document exists matching the filter."""
        doc = await self.collection.find_one(filter, {"_id": 1})
        return doc is not None
