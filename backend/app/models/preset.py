"""Custom preset model definitions."""

from typing import Any

from pydantic import Field

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin
from app.models.project import ProjectConfig


class PresetBase(StudioBaseModel):
    """Base preset model."""

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    config: ProjectConfig


class PresetCreate(PresetBase):
    """Model for creating a custom preset."""

    pass


class PresetUpdate(StudioBaseModel):
    """Model for updating a preset."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    config: ProjectConfig | None = None


class Preset(PresetBase, MongoBaseModel, TimestampMixin):
    """Custom preset model for API responses."""

    user_id: str
    is_system: bool = False


class PresetList(StudioBaseModel):
    """Paginated list of presets."""

    items: list[Preset]
    total: int
    page: int = 1
    page_size: int = 20


class PresetSummary(StudioBaseModel):
    """Summary of a preset for listing."""

    id: str
    name: str
    description: str
    is_system: bool = False
    is_custom: bool = True
