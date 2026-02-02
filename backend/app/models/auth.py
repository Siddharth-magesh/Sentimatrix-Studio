"""Authentication-related models."""

from pydantic import EmailStr, Field

from app.models.base import StudioBaseModel


class LoginRequest(StudioBaseModel):
    """Login request model."""

    email: EmailStr
    password: str


class TokenResponse(StudioBaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")


class RefreshTokenRequest(StudioBaseModel):
    """Refresh token request model."""

    refresh_token: str


class ForgotPasswordRequest(StudioBaseModel):
    """Forgot password request model."""

    email: EmailStr


class ResetPasswordRequest(StudioBaseModel):
    """Reset password request model."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(StudioBaseModel):
    """Generic message response."""

    message: str
