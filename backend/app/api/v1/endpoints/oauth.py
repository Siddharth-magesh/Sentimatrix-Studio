"""OAuth2 authentication endpoints."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.db.mongodb import MongoDB
from app.models.auth import TokenResponse
from app.models.user import User
from app.repositories.user import UserRepository, get_user_repository
from app.services.auth import AuthService, get_auth_service

logger = structlog.get_logger(__name__)

router = APIRouter()


# OAuth2 Provider configurations
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


def get_auth_service_dep(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    """Dependency to get auth service."""
    return get_auth_service(user_repo)


# ===========================================
# Google OAuth2
# ===========================================


@router.get(
    "/google",
    summary="Initiate Google OAuth2 login",
)
async def google_login(
    redirect_uri: str = Query(..., description="Callback URL after authentication"),
) -> dict:
    """
    Get the Google OAuth2 authorization URL.

    Redirect the user to this URL to start the authentication process.
    """
    settings = get_settings()

    if not settings.google_oauth_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth is not configured",
        )

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = f"{GOOGLE_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())

    return {"auth_url": auth_url}


@router.get(
    "/google/callback",
    response_model=TokenResponse,
    summary="Google OAuth2 callback",
)
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    redirect_uri: str = Query(..., description="Same redirect_uri used in authorization"),
    user_repo: Annotated[UserRepository, Depends(get_user_repository)] = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)] = None,
) -> TokenResponse:
    """
    Handle the Google OAuth2 callback.

    Exchange the authorization code for tokens and create/login the user.
    """
    settings = get_settings()

    if not settings.google_oauth_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth is not configured",
        )

    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            logger.error("Google token exchange failed", response=token_response.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # Get user info
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )

        userinfo = userinfo_response.json()

    email = userinfo.get("email")
    name = userinfo.get("name") or email.split("@")[0]

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google",
        )

    # Find or create user
    user = await _find_or_create_oauth_user(
        user_repo=user_repo,
        email=email,
        name=name,
        provider="google",
    )

    # Create tokens
    return await _create_tokens_for_user(user, auth_service)


# ===========================================
# GitHub OAuth2
# ===========================================


@router.get(
    "/github",
    summary="Initiate GitHub OAuth2 login",
)
async def github_login(
    redirect_uri: str = Query(..., description="Callback URL after authentication"),
) -> dict:
    """
    Get the GitHub OAuth2 authorization URL.

    Redirect the user to this URL to start the authentication process.
    """
    settings = get_settings()

    if not settings.github_oauth_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub OAuth is not configured",
        )

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
    }

    auth_url = f"{GITHUB_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())

    return {"auth_url": auth_url}


@router.get(
    "/github/callback",
    response_model=TokenResponse,
    summary="GitHub OAuth2 callback",
)
async def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    redirect_uri: str = Query(..., description="Same redirect_uri used in authorization"),
    user_repo: Annotated[UserRepository, Depends(get_user_repository)] = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service_dep)] = None,
) -> TokenResponse:
    """
    Handle the GitHub OAuth2 callback.

    Exchange the authorization code for tokens and create/login the user.
    """
    settings = get_settings()

    if not settings.github_oauth_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub OAuth is not configured",
        )

    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "code": code,
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "redirect_uri": redirect_uri,
            },
        )

        if token_response.status_code != 200:
            logger.error("GitHub token exchange failed", response=token_response.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from GitHub",
            )

        # Get user info
        user_response = await client.get(
            GITHUB_USER_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from GitHub",
            )

        user_data = user_response.json()

        # Get email (may be private)
        email = user_data.get("email")
        if not email:
            # Try to get primary email from emails endpoint
            emails_response = await client.get(
                GITHUB_EMAILS_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )

            if emails_response.status_code == 200:
                emails = emails_response.json()
                for email_obj in emails:
                    if email_obj.get("primary"):
                        email = email_obj.get("email")
                        break
                if not email and emails:
                    email = emails[0].get("email")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by GitHub. Please make your email public or add one.",
        )

    name = user_data.get("name") or user_data.get("login") or email.split("@")[0]

    # Find or create user
    user = await _find_or_create_oauth_user(
        user_repo=user_repo,
        email=email,
        name=name,
        provider="github",
    )

    # Create tokens
    return await _create_tokens_for_user(user, auth_service)


# ===========================================
# Helper Functions
# ===========================================


async def _find_or_create_oauth_user(
    user_repo: UserRepository,
    email: str,
    name: str,
    provider: str,
) -> User:
    """Find existing user or create a new one for OAuth."""
    # Check if user exists
    user = await user_repo.get_user_by_email(email)

    if user:
        # Update OAuth provider if not set
        if not user.oauth_provider and user.id:
            await user_repo.update(user.id, {"oauth_provider": provider})
        return user

    # Create new user (no password for OAuth users)
    import secrets
    from bson import ObjectId
    from datetime import datetime

    collection = MongoDB.get_collection("users")

    user_data = {
        "_id": ObjectId(),
        "email": email.lower(),
        "name": name,
        "password_hash": "",  # No password for OAuth users
        "is_active": True,
        "is_verified": True,  # OAuth users are verified by provider
        "role": "user",
        "oauth_provider": provider,
        "last_login": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    await collection.insert_one(user_data)

    logger.info("OAuth user created", email=email, provider=provider)

    return User(
        id=str(user_data["_id"]),
        email=email,
        name=name,
        is_active=True,
        is_verified=True,
        role="user",
        oauth_provider=provider,
        last_login=user_data["last_login"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"],
    )


async def _create_tokens_for_user(user: User, auth_service: AuthService) -> TokenResponse:
    """Create access and refresh tokens for a user."""
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid user",
        )

    settings = get_settings()

    access_token = create_access_token(
        subject=user.id,
        extra_data={"email": user.email, "role": user.role},
    )
    refresh_token = create_refresh_token(subject=user.id)

    # Store refresh token
    await auth_service._store_refresh_token(user.id, refresh_token)

    # Update last login
    await auth_service.user_repo.update_last_login(user.id)

    logger.info("OAuth login successful", user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get(
    "/providers",
    summary="List available OAuth providers",
)
async def list_oauth_providers() -> list[dict]:
    """
    Get list of available OAuth providers.

    Returns which providers are configured and available for use.
    """
    settings = get_settings()

    providers = []

    if settings.google_oauth_enabled:
        providers.append({
            "id": "google",
            "name": "Google",
            "enabled": True,
        })
    else:
        providers.append({
            "id": "google",
            "name": "Google",
            "enabled": False,
        })

    if settings.github_oauth_enabled:
        providers.append({
            "id": "github",
            "name": "GitHub",
            "enabled": True,
        })
    else:
        providers.append({
            "id": "github",
            "name": "GitHub",
            "enabled": False,
        })

    return providers
