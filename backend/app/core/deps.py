"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    UserNotFoundError,
)
from app.core.security import verify_access_token
from app.models.user import User
from app.repositories.user import UserRepository, get_user_repository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Get the current authenticated user from the JWT token."""
    if credentials is None:
        raise AuthenticationError("Authentication required")

    token = credentials.credentials

    try:
        payload = verify_access_token(token)
    except InvalidTokenError:
        raise

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token payload")

    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise UserNotFoundError()

    if not user.is_active:
        raise AuthenticationError("User account is deactivated")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise AuthenticationError("User account is deactivated")
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get the current verified user."""
    if not current_user.is_verified:
        raise AuthorizationError("Email verification required")
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Get the current user if they are an admin."""
    if current_user.role != "admin":
        raise AuthorizationError("Admin access required")
    return current_user


# Optional user dependency (returns None if not authenticated)
async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User | None:
    """Get the current user if authenticated, otherwise return None."""
    if credentials is None:
        return None

    try:
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id:
            return await user_repo.get_user_by_id(user_id)
    except Exception:
        pass

    return None
