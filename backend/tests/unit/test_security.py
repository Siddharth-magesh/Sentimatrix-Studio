"""Tests for JWT security module."""

import pytest
from datetime import datetime, timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    get_token_expiry,
)
from app.core.exceptions import InvalidTokenError, TokenExpiredError


class TestJWTSecurity:
    """Test JWT token operations."""

    def test_create_access_token(self):
        """Test creating an access token."""
        token = create_access_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_extra_data(self):
        """Test creating access token with extra data."""
        token = create_access_token(
            subject="user123",
            extra_data={"email": "test@example.com", "role": "admin"},
        )

        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        token = create_refresh_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)

        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_verify_access_token(self):
        """Test verifying valid access token."""
        token = create_access_token(subject="user123")
        payload = verify_access_token(token)

        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_verify_access_token_wrong_type(self):
        """Test verifying refresh token as access token."""
        token = create_refresh_token(subject="user123")

        with pytest.raises(InvalidTokenError):
            verify_access_token(token)

    def test_verify_refresh_token(self):
        """Test verifying valid refresh token."""
        token = create_refresh_token(subject="user123")
        payload = verify_refresh_token(token)

        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_verify_refresh_token_wrong_type(self):
        """Test verifying access token as refresh token."""
        token = create_access_token(subject="user123")

        with pytest.raises(InvalidTokenError):
            verify_refresh_token(token)

    def test_decode_invalid_token(self):
        """Test decoding invalid token."""
        with pytest.raises(InvalidTokenError):
            decode_token("invalid.token.here")

    def test_get_token_expiry(self):
        """Test getting token expiry."""
        token = create_access_token(subject="user123")
        expiry = get_token_expiry(token)

        assert expiry is not None
        assert expiry > datetime.utcnow()

    def test_get_token_expiry_invalid(self):
        """Test getting expiry of invalid token."""
        expiry = get_token_expiry("invalid.token.here")
        assert expiry is None
