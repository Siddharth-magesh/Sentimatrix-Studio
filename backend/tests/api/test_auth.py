"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_user_data: dict):
    """Test user registration."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"].lower()
    assert data["name"] == test_user_data["name"]
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user_data: dict):
    """Test registration with duplicate email."""
    # Register first user
    await client.post("/api/v1/auth/register", json=test_user_data)

    # Try to register again with same email
    response = await client.post("/api/v1/auth/register", json=test_user_data)

    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "EMAIL_EXISTS"


@pytest.mark.asyncio
async def test_register_invalid_password(client: AsyncClient):
    """Test registration with invalid password."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "weak",  # Too short, no uppercase, no digit
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email."""
    user_data = {
        "email": "not-an-email",
        "name": "Test User",
        "password": "TestPass123",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user_data: dict):
    """Test successful login."""
    # Register user first
    await client.post("/api/v1/auth/register", json=test_user_data)

    # Login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user_data: dict):
    """Test login with invalid credentials."""
    # Register user first
    await client.post("/api/v1/auth/register", json=test_user_data)

    # Login with wrong password
    login_data = {
        "email": test_user_data["email"],
        "password": "WrongPassword123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent user."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "TestPass123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user_data: dict):
    """Test getting current user info."""
    # Register and login
    await client.post("/api/v1/auth/register", json=test_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    tokens = login_response.json()

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"].lower()
    assert data["name"] == test_user_data["name"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without auth."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens(client: AsyncClient, test_user_data: dict):
    """Test refreshing tokens."""
    # Register and login
    await client.post("/api/v1/auth/register", json=test_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    tokens = login_response.json()

    # Refresh tokens
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] != tokens["access_token"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refreshing with invalid token."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, test_user_data: dict):
    """Test logout."""
    # Register and login
    await client.post("/api/v1/auth/register", json=test_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    tokens = login_response.json()

    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
