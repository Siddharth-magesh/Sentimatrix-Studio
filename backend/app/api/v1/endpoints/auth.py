"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_user
from app.models.auth import (
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
)
from app.models.user import User, UserCreate
from app.repositories.user import UserRepository, get_user_repository
from app.services.auth import AuthService, get_auth_service

router = APIRouter()


def get_auth_service_dep(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    """Dependency to get auth service."""
    return get_auth_service(user_repo)


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> User:
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **name**: User's display name
    - **password**: Password (min 8 chars, must contain uppercase, lowercase, and digit)
    """
    return await auth_service.register(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to get access tokens",
)
async def login(
    credentials: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> TokenResponse:
    """
    Authenticate and receive access tokens.

    Returns access token and refresh token for API authentication.
    """
    return await auth_service.login(credentials.email, credentials.password)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout and revoke tokens",
)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> MessageResponse:
    """
    Logout the current user and revoke the refresh token.

    Requires authentication.
    """
    if current_user.id:
        await auth_service.logout(current_user.id, refresh_data.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access tokens",
)
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> TokenResponse:
    """
    Get new access and refresh tokens using a valid refresh token.

    The old refresh token will be invalidated.
    """
    return await auth_service.refresh_tokens(refresh_data.refresh_token)


@router.get(
    "/me",
    response_model=User,
    summary="Get current user",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the currently authenticated user's information.

    Requires authentication.
    """
    return current_user
