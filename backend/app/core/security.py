"""JWT token generation and validation."""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError


def create_access_token(subject: str, extra_data: dict[str, Any] | None = None) -> str:
    """Create a JWT access token."""
    settings = get_settings()

    expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }

    if extra_data:
        to_encode.update(extra_data)

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token."""
    settings = get_settings()

    expires_delta = timedelta(days=settings.jwt_refresh_token_expire_days)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify an access token and return its payload."""
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")

    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Verify a refresh token and return its payload."""
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")

    return payload


def get_token_expiry(token: str) -> datetime | None:
    """Get the expiry time of a token."""
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except Exception:
        return None


def create_password_reset_token(email: str) -> str:
    """Create a password reset token."""
    settings = get_settings()

    # Token expires in 1 hour
    expires_delta = timedelta(hours=1)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset",
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_password_reset_token(token: str) -> str:
    """Verify a password reset token and return the email."""
    payload = decode_token(token)

    if payload.get("type") != "password_reset":
        raise InvalidTokenError("Invalid token type")

    email = payload.get("sub")
    if not email:
        raise InvalidTokenError("Invalid token")

    return email


def create_email_verification_token(email: str) -> str:
    """Create an email verification token."""
    settings = get_settings()

    # Token expires in 24 hours
    expires_delta = timedelta(hours=24)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "email_verification",
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_email_verification_token(token: str) -> str:
    """Verify an email verification token and return the email."""
    payload = decode_token(token)

    if payload.get("type") != "email_verification":
        raise InvalidTokenError("Invalid token type")

    email = payload.get("sub")
    if not email:
        raise InvalidTokenError("Invalid token")

    return email
