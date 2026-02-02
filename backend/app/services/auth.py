"""Authentication service with business logic."""

import hashlib
from datetime import datetime, timedelta

import structlog
from bson import ObjectId

from app.core.config import get_settings
from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenBlacklistedError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.db.mongodb import MongoDB
from app.models.auth import TokenResponse
from app.models.user import User, UserCreate
from app.repositories.user import UserRepository

logger = structlog.get_logger(__name__)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        logger.info("Registering new user", email=user_data.email)

        user = await self.user_repo.create_user(user_data)

        logger.info("User registered successfully", user_id=user.id)
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens."""
        logger.info("Login attempt", email=email)

        user = await self.user_repo.authenticate(email, password)
        if not user:
            logger.warning("Failed login attempt", email=email)
            raise InvalidCredentialsError()

        if not user.id:
            raise InvalidCredentialsError()

        # Create tokens
        access_token = create_access_token(
            subject=user.id,
            extra_data={"email": user.email, "role": user.role},
        )
        refresh_token = create_refresh_token(subject=user.id)

        # Store refresh token
        await self._store_refresh_token(user.id, refresh_token)

        settings = get_settings()

        logger.info("User logged in successfully", user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def logout(self, user_id: str, refresh_token: str) -> None:
        """Logout user by blacklisting the refresh token."""
        logger.info("Logging out user", user_id=user_id)

        # Remove refresh token
        await self._revoke_refresh_token(refresh_token)

        logger.info("User logged out successfully", user_id=user_id)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        # Verify refresh token
        try:
            payload = verify_refresh_token(refresh_token)
        except Exception:
            raise InvalidTokenError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Invalid refresh token")

        # Check if token is blacklisted
        if await self._is_token_revoked(refresh_token):
            raise TokenBlacklistedError()

        # Get user
        user = await self.user_repo.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidTokenError("User not found or inactive")

        # Revoke old refresh token
        await self._revoke_refresh_token(refresh_token)

        # Create new tokens
        new_access_token = create_access_token(
            subject=user_id,
            extra_data={"email": user.email, "role": user.role},
        )
        new_refresh_token = create_refresh_token(subject=user_id)

        # Store new refresh token
        await self._store_refresh_token(user_id, new_refresh_token)

        settings = get_settings()

        logger.info("Tokens refreshed", user_id=user_id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def _store_refresh_token(self, user_id: str, token: str) -> None:
        """Store refresh token in database."""
        settings = get_settings()
        collection = MongoDB.get_collection("refresh_tokens")

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)

        await collection.insert_one(
            {
                "user_id": ObjectId(user_id),
                "token_hash": token_hash,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
            }
        )

    async def _revoke_refresh_token(self, token: str) -> None:
        """Revoke a refresh token."""
        collection = MongoDB.get_collection("refresh_tokens")
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        await collection.delete_one({"token_hash": token_hash})

    async def _is_token_revoked(self, token: str) -> bool:
        """Check if a refresh token has been revoked."""
        collection = MongoDB.get_collection("refresh_tokens")
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        doc = await collection.find_one({"token_hash": token_hash})
        return doc is None

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        collection = MongoDB.get_collection("refresh_tokens")
        await collection.delete_many({"user_id": ObjectId(user_id)})
        logger.info("All tokens revoked for user", user_id=user_id)


def get_auth_service(user_repo: UserRepository) -> AuthService:
    """Create auth service instance."""
    return AuthService(user_repo)
