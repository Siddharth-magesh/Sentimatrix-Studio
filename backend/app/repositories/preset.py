"""Custom preset repository for database operations."""

from bson import ObjectId

from app.core.exceptions import NotFoundError, ConflictError
from app.models.preset import Preset, PresetCreate, PresetUpdate, PresetList
from app.repositories.base import BaseRepository


class PresetRepository(BaseRepository[Preset]):
    """Repository for custom preset database operations."""

    collection_name = "presets"
    model_class = Preset

    async def create_preset(
        self,
        user_id: str,
        preset_data: PresetCreate,
    ) -> Preset:
        """Create a new custom preset."""
        # Check for duplicate name
        existing = await self.get_one({
            "user_id": ObjectId(user_id),
            "name": preset_data.name,
        })
        if existing:
            raise ConflictError(f"Preset with name '{preset_data.name}' already exists")

        data = {
            "user_id": ObjectId(user_id),
            "name": preset_data.name,
            "description": preset_data.description,
            "config": preset_data.config.model_dump(),
            "is_system": False,
        }

        return await self.create(data)

    async def get_preset(self, preset_id: str, user_id: str) -> Preset:
        """Get a preset by ID."""
        preset = await self.get_one({
            "_id": ObjectId(preset_id),
            "user_id": ObjectId(user_id),
        })

        if not preset:
            raise NotFoundError("Preset not found")

        return preset

    async def get_presets(self, user_id: str) -> PresetList:
        """Get all custom presets for a user."""
        query = {"user_id": ObjectId(user_id)}

        presets = await self.get_many(query, sort=[("created_at", -1)])
        total = await self.count(query)

        return PresetList(
            items=presets,
            total=total,
            page=1,
            page_size=total or 20,
        )

    async def update_preset(
        self,
        preset_id: str,
        user_id: str,
        update_data: PresetUpdate,
    ) -> Preset:
        """Update a custom preset."""
        # Verify ownership
        preset = await self.get_preset(preset_id, user_id)

        if preset.is_system:
            raise ConflictError("Cannot modify system presets")

        # Check for duplicate name if name is being changed
        if update_data.name and update_data.name != preset.name:
            existing = await self.get_one({
                "user_id": ObjectId(user_id),
                "name": update_data.name,
                "_id": {"$ne": ObjectId(preset_id)},
            })
            if existing:
                raise ConflictError(f"Preset with name '{update_data.name}' already exists")

        # Build update dict
        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.description is not None:
            update_dict["description"] = update_data.description
        if update_data.config is not None:
            update_dict["config"] = update_data.config.model_dump()

        if not update_dict:
            return preset

        updated = await self.update(preset_id, update_dict)
        if not updated:
            raise NotFoundError("Preset not found")

        return updated

    async def delete_preset(self, preset_id: str, user_id: str) -> None:
        """Delete a custom preset."""
        # Verify ownership
        preset = await self.get_preset(preset_id, user_id)

        if preset.is_system:
            raise ConflictError("Cannot delete system presets")

        await self.delete(preset_id)

    async def duplicate_preset(
        self,
        preset_id: str,
        user_id: str,
        new_name: str | None = None,
    ) -> Preset:
        """Duplicate a preset."""
        preset = await self.get_preset(preset_id, user_id)

        # Generate new name
        name = new_name or f"{preset.name} (Copy)"

        # Create duplicate
        data = {
            "user_id": ObjectId(user_id),
            "name": name,
            "description": preset.description,
            "config": preset.config.model_dump() if hasattr(preset.config, 'model_dump') else preset.config,
            "is_system": False,
        }

        return await self.create(data)


def get_preset_repository() -> PresetRepository:
    """FastAPI dependency to get preset repository."""
    return PresetRepository()
