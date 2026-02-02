"""User model definitions."""

from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class UserBase(StudioBaseModel):
    """Base user model with common fields."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean the name."""
        return v.strip()


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(StudioBaseModel):
    """Model for updating a user."""

    name: str | None = Field(default=None, min_length=1, max_length=100)


class UserPasswordUpdate(StudioBaseModel):
    """Model for updating user password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class User(UserBase, MongoBaseModel, TimestampMixin):
    """User model for API responses."""

    is_active: bool = True
    is_verified: bool = False
    role: Literal["user", "admin"] = "user"
    oauth_provider: str | None = None
    last_login: datetime | None = None


class UserInDB(User):
    """User model with database-specific fields."""

    password_hash: str
