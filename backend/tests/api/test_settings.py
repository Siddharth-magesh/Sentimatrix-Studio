"""Tests for settings API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user_data: dict) -> dict:
    """Get auth headers for authenticated requests."""
    await client.post("/api/v1/auth/register", json=test_user_data)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


class TestLLMProviders:
    """Test LLM provider endpoints."""

    @pytest.mark.asyncio
    async def test_list_providers(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing LLM providers."""
        response = await client.get(
            "/api/v1/settings/llm/providers",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        provider_ids = [p["id"] for p in data]
        assert "groq" in provider_ids
        assert "openai" in provider_ids
        assert "anthropic" in provider_ids

    @pytest.mark.asyncio
    async def test_get_provider_details(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting provider details."""
        response = await client.get(
            "/api/v1/settings/llm/providers/groq",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "groq"
        assert data["name"] == "Groq"
        assert len(data["models"]) > 0

    @pytest.mark.asyncio
    async def test_get_provider_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting non-existent provider."""
        response = await client.get(
            "/api/v1/settings/llm/providers/invalid",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestAPIKeys:
    """Test API key management endpoints."""

    @pytest.mark.asyncio
    async def test_add_api_key(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test adding an API key."""
        response = await client.post(
            "/api/v1/settings/api-keys",
            json={
                "provider": "groq",
                "api_key": "gsk_test_api_key_12345",
                "label": "My Groq Key",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "groq"
        assert data["label"] == "My Groq Key"
        assert "..." in data["masked_key"]  # Should be masked
        assert "12345" not in data["masked_key"]  # Full key not exposed

    @pytest.mark.asyncio
    async def test_list_api_keys(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing API keys."""
        # Add keys first
        await client.post(
            "/api/v1/settings/api-keys",
            json={"provider": "groq", "api_key": "gsk_test_key"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/settings/api-keys",
            json={"provider": "openai", "api_key": "sk_test_key"},
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/settings/api-keys",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        providers = [k["provider"] for k in data]
        assert "groq" in providers
        assert "openai" in providers

    @pytest.mark.asyncio
    async def test_delete_api_key(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test deleting an API key."""
        # Add key
        await client.post(
            "/api/v1/settings/api-keys",
            json={"provider": "groq", "api_key": "gsk_test_key"},
            headers=auth_headers,
        )

        # Delete key
        response = await client.delete(
            "/api/v1/settings/api-keys/groq",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        list_response = await client.get(
            "/api/v1/settings/api-keys",
            headers=auth_headers,
        )
        assert len(list_response.json()) == 0

    @pytest.mark.asyncio
    async def test_add_api_key_invalid_provider(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test adding API key with invalid provider."""
        response = await client.post(
            "/api/v1/settings/api-keys",
            json={"provider": "invalid", "api_key": "test_key"},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error


class TestPresets:
    """Test preset endpoints."""

    @pytest.mark.asyncio
    async def test_list_presets(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing presets."""
        response = await client.get(
            "/api/v1/settings/presets",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
        preset_ids = [p["id"] for p in data]
        assert "starter" in preset_ids
        assert "standard" in preset_ids
        assert "advanced" in preset_ids

    @pytest.mark.asyncio
    async def test_get_preset_details(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting preset details."""
        response = await client.get(
            "/api/v1/settings/presets/advanced",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "advanced"
        assert "config" in data
        assert data["config"]["analysis"]["sentiment_classes"] == 5

    @pytest.mark.asyncio
    async def test_get_preset_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting non-existent preset."""
        response = await client.get(
            "/api/v1/settings/presets/nonexistent",
            headers=auth_headers,
        )

        assert response.status_code == 404
