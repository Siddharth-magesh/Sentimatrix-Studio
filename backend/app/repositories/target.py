"""Target repository for database operations."""

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from bson import ObjectId

from app.core.exceptions import NotFoundError, TargetNotFoundError, ValidationError
from app.models.target import (
    Target,
    TargetCreate,
    TargetBulkCreate,
    TargetInDB,
    TargetList,
    TargetUpdate,
    PlatformData,
    TargetStats,
)
from app.repositories.base import BaseRepository


# Platform detection patterns
PLATFORM_PATTERNS = {
    "amazon": [
        r"amazon\.(com|co\.uk|de|fr|it|es|ca|com\.au|co\.jp|in)",
        r"amzn\.(to|com)",
    ],
    "steam": [
        r"store\.steampowered\.com",
        r"steamcommunity\.com",
    ],
    "youtube": [
        r"youtube\.com",
        r"youtu\.be",
    ],
    "reddit": [
        r"reddit\.com",
        r"old\.reddit\.com",
    ],
    "google": [
        r"google\.(com|co\.\w+)/maps",
        r"maps\.google",
    ],
    "trustpilot": [
        r"trustpilot\.com",
    ],
    "yelp": [
        r"yelp\.(com|co\.\w+)",
    ],
}


def detect_platform(url: str) -> str | None:
    """Detect platform from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, domain):
                return platform

    return None


def extract_platform_data(url: str, platform: str) -> PlatformData:
    """Extract platform-specific data from URL."""
    data = PlatformData()
    parsed = urlparse(url)
    path = parsed.path

    if platform == "amazon":
        # Extract ASIN from Amazon URL
        asin_match = re.search(r"/dp/([A-Z0-9]{10})", path)
        if asin_match:
            data.asin = asin_match.group(1)

    elif platform == "steam":
        # Extract app ID from Steam URL
        app_match = re.search(r"/app/(\d+)", path)
        if app_match:
            data.app_id = int(app_match.group(1))

    elif platform == "youtube":
        # Extract video ID
        if "youtu.be" in parsed.netloc:
            data.video_id = path.strip("/")
        else:
            video_match = re.search(r"[?&]v=([^&]+)", parsed.query or "")
            if video_match:
                data.video_id = video_match.group(1)

    elif platform == "reddit":
        # Extract post ID
        post_match = re.search(r"/comments/([a-z0-9]+)", path)
        if post_match:
            data.post_id = post_match.group(1)

    return data


class TargetRepository(BaseRepository[TargetInDB]):
    """Repository for target database operations."""

    collection_name = "targets"
    model_class = TargetInDB

    async def create_target(
        self, project_id: str, user_id: str, target_data: TargetCreate
    ) -> Target:
        """Create a new target."""
        # Detect platform
        platform = detect_platform(target_data.url)
        platform_data = PlatformData()

        if platform:
            platform_data = extract_platform_data(target_data.url, platform)

        # Determine detected type based on platform
        detected_type = None
        if platform == "amazon":
            detected_type = "product"
        elif platform == "steam":
            detected_type = "game"
        elif platform == "youtube":
            detected_type = "video"
        elif platform == "reddit":
            detected_type = "post"
        elif platform in ("google", "trustpilot", "yelp"):
            detected_type = "business"

        data = {
            "project_id": project_id,
            "user_id": user_id,
            "url": target_data.url,
            "label": target_data.label or self._generate_label(target_data.url, platform),
            "platform": platform,
            "detected_type": detected_type,
            "platform_data": platform_data.model_dump(),
            "options": (target_data.options.model_dump() if target_data.options else {}),
            "metadata": target_data.metadata or {},
            "stats": TargetStats().model_dump(),
            "status": "active",
            "error_message": None,
        }

        target_in_db = await self.create(data)
        return self._to_target(target_in_db)

    async def create_targets_bulk(
        self, project_id: str, user_id: str, bulk_data: TargetBulkCreate
    ) -> list[Target]:
        """Create multiple targets at once."""
        targets = []
        for url in bulk_data.urls:
            target_data = TargetCreate(url=url, options=bulk_data.options)
            target = await self.create_target(project_id, user_id, target_data)
            targets.append(target)
        return targets

    async def get_target(
        self, target_id: str, user_id: str | None = None
    ) -> Target:
        """Get a target by ID."""
        filter_dict: dict[str, Any] = {"_id": ObjectId(target_id)}
        if user_id:
            filter_dict["user_id"] = user_id

        target_in_db = await self.get_one(filter_dict)
        if not target_in_db:
            raise TargetNotFoundError()

        return self._to_target(target_in_db)

    async def get_targets_by_project(
        self,
        project_id: str,
        user_id: str | None = None,
        status: str | None = None,
    ) -> TargetList:
        """Get all targets for a project."""
        filter_dict: dict[str, Any] = {"project_id": project_id}
        if user_id:
            filter_dict["user_id"] = user_id
        if status:
            filter_dict["status"] = status

        total = await self.count(filter_dict)
        targets_in_db = await self.get_many(
            filter_dict,
            sort=[("created_at", -1)],
        )

        return TargetList(
            items=[self._to_target(t) for t in targets_in_db],
            total=total,
        )

    async def update_target(
        self, target_id: str, user_id: str, update_data: TargetUpdate
    ) -> Target:
        """Update a target."""
        await self.get_target(target_id, user_id)

        data = update_data.model_dump(exclude_unset=True)

        if "options" in data and data["options"]:
            data["options"] = data["options"]

        target_in_db = await self.update(target_id, data)
        if not target_in_db:
            raise TargetNotFoundError()

        return self._to_target(target_in_db)

    async def delete_target(self, target_id: str, user_id: str) -> bool:
        """Delete a target."""
        await self.get_target(target_id, user_id)
        return await self.delete(target_id)

    async def delete_targets_by_project(self, project_id: str) -> int:
        """Delete all targets for a project."""
        result = await self.collection.delete_many({"project_id": project_id})
        return result.deleted_count

    async def update_stats(
        self, target_id: str, stats_update: dict[str, Any]
    ) -> None:
        """Update target statistics."""
        update_dict = {f"stats.{k}": v for k, v in stats_update.items()}
        await self.collection.update_one(
            {"_id": ObjectId(target_id)},
            {"$set": update_dict},
        )

    async def set_error(self, target_id: str, error_message: str) -> None:
        """Set target error status."""
        await self.collection.update_one(
            {"_id": ObjectId(target_id)},
            {"$set": {"status": "error", "error_message": error_message}},
        )

    async def clear_error(self, target_id: str) -> None:
        """Clear target error status."""
        await self.collection.update_one(
            {"_id": ObjectId(target_id)},
            {"$set": {"status": "active", "error_message": None}},
        )

    def _generate_label(self, url: str, platform: str | None) -> str:
        """Generate a label from URL."""
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if platform == "amazon" and "/dp/" in path:
            return f"Amazon Product"
        elif platform == "steam" and "/app/" in path:
            return f"Steam Game"
        elif platform == "youtube":
            return f"YouTube Video"
        elif platform == "reddit":
            return f"Reddit Post"
        elif platform:
            return f"{platform.title()} Target"

        # Fallback to domain
        return parsed.netloc[:50] if parsed.netloc else url[:50]

    def _to_target(self, target_in_db: TargetInDB) -> Target:
        """Convert TargetInDB to Target."""
        return Target(
            id=target_in_db.id,
            project_id=target_in_db.project_id,
            user_id=target_in_db.user_id,
            url=target_in_db.url,
            label=target_in_db.label,
            platform=target_in_db.platform,
            detected_type=target_in_db.detected_type,
            platform_data=target_in_db.platform_data,
            options=target_in_db.options,
            metadata=target_in_db.metadata,
            stats=target_in_db.stats,
            status=target_in_db.status,
            error_message=target_in_db.error_message,
            created_at=target_in_db.created_at,
            updated_at=target_in_db.updated_at,
        )


def get_target_repository() -> TargetRepository:
    """FastAPI dependency to get target repository."""
    return TargetRepository()
