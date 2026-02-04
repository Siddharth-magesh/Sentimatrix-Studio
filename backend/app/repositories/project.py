"""Project repository for database operations."""

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.core.exceptions import NotFoundError, ProjectNotFoundError
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectInDB,
    ProjectList,
    ProjectUpdate,
    ProjectConfig,
    ProjectStats,
    PlatformLinks,
)
from app.repositories.base import BaseRepository
from app.services.presets import get_preset_config


class ProjectRepository(BaseRepository[ProjectInDB]):
    """Repository for project database operations."""

    collection_name = "projects"
    model_class = ProjectInDB

    async def create_project(
        self, user_id: str, project_data: ProjectCreate
    ) -> Project:
        """Create a new project with preset configuration."""
        # Get preset configuration if not custom
        config = project_data.config
        if config is None and project_data.preset != "custom":
            config = get_preset_config(project_data.preset)

        if config is None:
            config = ProjectConfig()

        # Handle product info
        product = None
        if project_data.product:
            product = project_data.product.model_dump()

        # Handle platform links
        platform_links = PlatformLinks()
        if project_data.platform_links:
            platform_links = project_data.platform_links

        data = {
            "user_id": user_id,
            "name": project_data.name,
            "description": project_data.description,
            "preset": project_data.preset,
            "status": "active",
            "product": product,
            "platform_links": platform_links.model_dump(),
            "config": config.model_dump(),
            "stats": ProjectStats().model_dump(),
            "archived_at": None,
        }

        project_in_db = await self.create(data)
        return self._to_project(project_in_db)

    async def get_project(self, project_id: str, user_id: str | None = None) -> Project:
        """Get a project by ID, optionally filtered by user."""
        filter_dict: dict[str, Any] = {"_id": ObjectId(project_id)}
        if user_id:
            filter_dict["user_id"] = user_id

        project_in_db = await self.get_one(filter_dict)
        if not project_in_db:
            raise ProjectNotFoundError()

        return self._to_project(project_in_db)

    async def get_projects(
        self,
        user_id: str,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ProjectList:
        """Get paginated list of projects for a user."""
        filter_dict: dict[str, Any] = {"user_id": user_id}

        if status:
            filter_dict["status"] = status

        if search:
            filter_dict["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        # Get total count
        total = await self.count(filter_dict)

        # Calculate pagination
        skip = (page - 1) * page_size
        pages = (total + page_size - 1) // page_size if total > 0 else 1

        # Get projects
        projects_in_db = await self.get_many(
            filter_dict,
            skip=skip,
            limit=page_size,
            sort=[("created_at", -1)],
        )

        return ProjectList(
            items=[self._to_project(p) for p in projects_in_db],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def update_project(
        self, project_id: str, user_id: str, update_data: ProjectUpdate
    ) -> Project:
        """Update a project."""
        # Verify ownership
        await self.get_project(project_id, user_id)

        data = update_data.model_dump(exclude_unset=True)

        # Handle config update
        if "config" in data and data["config"]:
            data["config"] = data["config"]

        # Handle archiving
        if data.get("status") == "archived":
            data["archived_at"] = datetime.utcnow()

        project_in_db = await self.update(project_id, data)
        if not project_in_db:
            raise ProjectNotFoundError()

        return self._to_project(project_in_db)

    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project (soft delete by archiving)."""
        await self.get_project(project_id, user_id)

        await self.update(
            project_id,
            {"status": "archived", "archived_at": datetime.utcnow()},
        )
        return True

    async def hard_delete_project(self, project_id: str, user_id: str) -> bool:
        """Permanently delete a project."""
        await self.get_project(project_id, user_id)
        return await self.delete(project_id)

    async def update_stats(self, project_id: str, stats_update: dict[str, Any]) -> None:
        """Update project statistics."""
        update_dict = {f"stats.{k}": v for k, v in stats_update.items()}
        await self.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_dict},
        )

    async def increment_stats(
        self, project_id: str, field: str, amount: int = 1
    ) -> None:
        """Increment a stats field."""
        await self.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$inc": {f"stats.{field}": amount}},
        )

    async def get_scheduled_projects(self) -> list[Project]:
        """Get projects with enabled schedules that are due."""
        filter_dict = {
            "status": "active",
            "config.schedule.enabled": True,
            "config.schedule.next_run_at": {"$lte": datetime.utcnow()},
        }

        projects_in_db = await self.get_many(filter_dict, limit=100)
        return [self._to_project(p) for p in projects_in_db]

    def _to_project(self, project_in_db: ProjectInDB) -> Project:
        """Convert ProjectInDB to Project."""
        return Project(
            id=project_in_db.id,
            user_id=project_in_db.user_id,
            name=project_in_db.name,
            description=project_in_db.description,
            status=project_in_db.status,
            preset=project_in_db.preset,
            product=project_in_db.product,
            platform_links=project_in_db.platform_links,
            config=project_in_db.config,
            stats=project_in_db.stats,
            archived_at=project_in_db.archived_at,
            created_at=project_in_db.created_at,
            updated_at=project_in_db.updated_at,
        )


def get_project_repository() -> ProjectRepository:
    """FastAPI dependency to get project repository."""
    return ProjectRepository()
