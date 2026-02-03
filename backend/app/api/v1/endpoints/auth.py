"""Authentication endpoints."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_user
from app.core.security import (
    create_password_reset_token,
    verify_password_reset_token,
)
from app.models.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.models.user import User, UserCreate, UserUpdate, UserPasswordUpdate
from app.repositories.user import UserRepository, get_user_repository
from app.services.auth import AuthService, get_auth_service

logger = structlog.get_logger(__name__)

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


@router.put(
    "/me",
    response_model=User,
    summary="Update current user profile",
)
async def update_me(
    update_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """
    Update the current user's profile information.

    - **name**: New display name (optional)
    """
    if not current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid user")

    updated_user = await user_repo.update_user(current_user.id, update_data)
    if not updated_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    logger.info("User profile updated", user_id=current_user.id)
    return updated_user


@router.put(
    "/me/password",
    response_model=MessageResponse,
    summary="Update password",
)
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> MessageResponse:
    """
    Update the current user's password.

    Requires the current password for verification.

    - **current_password**: Current password (required)
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, digit)
    """
    if not current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid user")

    success = await user_repo.update_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password,
    )

    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    logger.info("User password updated", user_id=current_user.id)
    return MessageResponse(message="Password updated successfully")


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account",
)
async def delete_account(
    current_user: Annotated[User, Depends(get_current_user)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)],
) -> None:
    """
    Delete the current user's account.

    This action is irreversible. All user data will be permanently deleted.
    """
    if not current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid user")

    # Revoke all tokens
    await auth_service.revoke_all_user_tokens(current_user.id)

    # Deactivate account (soft delete)
    await user_repo.deactivate_user(current_user.id)

    logger.info("User account deleted", user_id=current_user.id)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> MessageResponse:
    """
    Request a password reset email.

    If the email exists, a password reset link will be sent.
    For security, this endpoint always returns success even if the email doesn't exist.

    - **email**: Email address to send reset link to
    """
    user = await user_repo.get_user_by_email(request.email)

    if user:
        # Generate password reset token
        reset_token = create_password_reset_token(request.email)

        # In production, send email with reset link
        # For now, log the token (in development) or use email service
        logger.info(
            "Password reset requested",
            email=request.email,
            token=reset_token,  # Remove in production, send via email instead
        )

        # TODO: Integrate with email service (SendGrid, SES, etc.)
        # await send_password_reset_email(request.email, reset_token)

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password with token",
)
async def reset_password(
    request: ResetPasswordRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> MessageResponse:
    """
    Reset password using the token from the password reset email.

    - **token**: Password reset token from email
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, digit)
    """
    from fastapi import HTTPException

    try:
        email = verify_password_reset_token(request.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = await user_repo.get_user_by_email(email)
    if not user or not user.id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Set new password
    success = await user_repo.set_password(user.id, request.new_password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset password")

    logger.info("Password reset successful", user_id=user.id)
    return MessageResponse(message="Password has been reset successfully")
