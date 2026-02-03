"""Tests for webhook API endpoints."""

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


class TestWebhooks:
    """Test webhook endpoints."""

    @pytest.mark.asyncio
    async def test_create_webhook(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating a webhook."""
        response = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://example.com/webhook",
                "events": ["job.completed", "job.failed"],
                "secret": "my-secret",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com/webhook"
        assert len(data["events"]) == 2
        assert data["enabled"] is True

    @pytest.mark.asyncio
    async def test_create_webhook_invalid_url(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating webhook with invalid URL."""
        response = await client.post(
            "/api/v1/webhooks",
            json={"url": "not-a-url", "events": ["job.completed"]},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_webhook_invalid_event(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating webhook with invalid event."""
        response = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["invalid.event"]},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_webhooks(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing webhooks."""
        # Create webhooks
        await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example1.com/webhook", "events": ["job.completed"]},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example2.com/webhook", "events": ["job.failed"]},
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/webhooks",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_get_webhook(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting a specific webhook."""
        # Create webhook
        create_response = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["job.completed"]},
            headers=auth_headers,
        )
        webhook_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/webhooks/{webhook_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == webhook_id

    @pytest.mark.asyncio
    async def test_update_webhook(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test updating a webhook."""
        # Create webhook
        create_response = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["job.completed"]},
            headers=auth_headers,
        )
        webhook_id = create_response.json()["id"]

        # Update webhook
        response = await client.put(
            f"/api/v1/webhooks/{webhook_id}",
            json={"events": ["job.completed", "job.failed", "job.started"]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 3

    @pytest.mark.asyncio
    async def test_delete_webhook(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test deleting a webhook."""
        # Create webhook
        create_response = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["job.completed"]},
            headers=auth_headers,
        )
        webhook_id = create_response.json()["id"]

        # Delete webhook
        response = await client.delete(
            f"/api/v1/webhooks/{webhook_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(
            f"/api/v1/webhooks/{webhook_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_webhook(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test toggling webhook enabled status."""
        # Create webhook
        create_response = await client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/webhook", "events": ["job.completed"]},
            headers=auth_headers,
        )
        webhook_id = create_response.json()["id"]
        assert create_response.json()["enabled"] is True

        # Toggle off
        response = await client.post(
            f"/api/v1/webhooks/{webhook_id}/toggle",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["enabled"] is False

        # Toggle on
        response = await client.post(
            f"/api/v1/webhooks/{webhook_id}/toggle",
            headers=auth_headers,
        )

        assert response.json()["enabled"] is True

    @pytest.mark.asyncio
    async def test_list_available_events(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing available webhook events."""
        response = await client.get(
            "/api/v1/webhooks/events/available",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        events = [e["event"] for e in data]
        assert "job.completed" in events
        assert "job.failed" in events
        assert "job.started" in events
