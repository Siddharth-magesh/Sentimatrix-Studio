"""User repository for database operations."""

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.core.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.models.user import User, UserCreate, UserInDB, UserUpdate
from app.repositories.base import BaseRepository
from app.utils.password import hash_password, verify_password


class UserRepository(BaseRepository[UserInDB]):
    """Repository for user database operations."""

    collection_name = "users"
    model_class = UserInDB

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Check if email already exists
        if await self.email_exists(user_data.email):
            raise EmailAlreadyExistsError()

        # Hash password and prepare data
        data = {
            "email": user_data.email.lower(),
            "name": user_data.name,
            "password_hash": hash_password(user_data.password),
            "is_active": True,
            "is_verified": False,
            "role": "user",
            "oauth_provider": None,
            "last_login": None,
        }

        user_in_db = await self.create(data)
        return self._to_user(user_in_db)

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by ID (without password hash)."""
        user_in_db = await self.get_by_id(user_id)
        if user_in_db:
            return self._to_user(user_in_db)
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email (without password hash)."""
        user_in_db = await self.get_one({"email": email.lower()})
        if user_in_db:
            return self._to_user(user_in_db)
        return None

    async def get_user_with_password(self, email: str) -> UserInDB | None:
        """Get a user by email with password hash for authentication."""
        return await self.get_one({"email": email.lower()})

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User | None:
        """Update user information."""
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user_by_id(user_id)

        user_in_db = await self.update(user_id, update_data)
        if user_in_db:
            return self._to_user(user_in_db)
        return None

    async def update_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Update user password after verifying current password."""
        user_in_db = await self.get_by_id(user_id)
        if not user_in_db:
            raise UserNotFoundError()

        if not verify_password(current_password, user_in_db.password_hash):
            return False

        await self.update(user_id, {"password_hash": hash_password(new_password)})
        return True

    async def set_password(self, user_id: str, new_password: str) -> bool:
        """Set user password (for password reset)."""
        result = await self.update(user_id, {"password_hash": hash_password(new_password)})
        return result is not None

    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        await self.update(user_id, {"last_login": datetime.utcnow()})

    async def verify_user(self, user_id: str) -> bool:
        """Mark user as verified."""
        result = await self.update(user_id, {"is_verified": True})
        return result is not None

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        result = await self.update(user_id, {"is_active": False})
        return result is not None

    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        result = await self.update(user_id, {"is_active": True})
        return result is not None

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        return await self.exists({"email": email.lower()})

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user_in_db = await self.get_user_with_password(email)
        if not user_in_db:
            return None

        if not verify_password(password, user_in_db.password_hash):
            return None

        if not user_in_db.is_active:
            return None

        # Update last login
        if user_in_db.id:
            await self.update_last_login(user_in_db.id)

        return self._to_user(user_in_db)

    def _to_user(self, user_in_db: UserInDB) -> User:
        """Convert UserInDB to User (removing password hash)."""
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            name=user_in_db.name,
            is_active=user_in_db.is_active,
            is_verified=user_in_db.is_verified,
            role=user_in_db.role,
            oauth_provider=user_in_db.oauth_provider,
            last_login=user_in_db.last_login,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at,
        )


def get_user_repository() -> UserRepository:
    """FastAPI dependency to get user repository."""
    return UserRepository()
