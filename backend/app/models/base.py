"""Base model classes with common functionality."""

from datetime import datetime
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator, _field_schema):
        return {"type": "string"}


class StudioBaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        from_attributes=True,
    )


class MongoBaseModel(StudioBaseModel):
    """Base model for MongoDB documents."""

    model_config = ConfigDict(populate_by_name=True)

    id: Annotated[str | None, Field(alias="_id", default=None)]

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)

    @field_serializer("id", when_used="always")
    def serialize_id(self, v: str | None) -> str | None:
        return v


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
