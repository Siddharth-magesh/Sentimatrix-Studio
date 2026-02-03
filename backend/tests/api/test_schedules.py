"""Tests for schedule API endpoints."""

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


@pytest.fixture
async def project_id(client: AsyncClient, auth_headers: dict) -> str:
    """Create a project and return its ID."""
    response = await client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "preset": "standard"},
        headers=auth_headers,
    )
    return response.json()["id"]


class TestSchedules:
    """Test schedule endpoints."""

    @pytest.mark.asyncio
    async def test_create_schedule(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating a schedule."""
        response = await client.post(
            "/api/v1/schedules",
            json={
                "project_id": project_id,
                "frequency": "daily",
                "time": "09:00",
                "timezone": "UTC",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == project_id
        assert data["frequency"] == "daily"
        assert data["time"] == "09:00"
        assert data["enabled"] is True
        assert data["next_run"] is not None

    @pytest.mark.asyncio
    async def test_create_schedule_weekly(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating a weekly schedule."""
        response = await client.post(
            "/api/v1/schedules",
            json={
                "project_id": project_id,
                "frequency": "weekly",
                "time": "10:00",
                "day_of_week": 1,  # Tuesday
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "weekly"
        assert data["day_of_week"] == 1

    @pytest.mark.asyncio
    async def test_create_schedule_duplicate(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating duplicate schedule fails."""
        # Create first schedule
        await client.post(
            "/api/v1/schedules",
            json={"project_id": project_id, "frequency": "daily"},
            headers=auth_headers,
        )

        # Try to create second schedule
        response = await client.post(
            "/api/v1/schedules",
            json={"project_id": project_id, "frequency": "weekly"},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_project_schedule(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test getting a project's schedule."""
        # Create schedule
        await client.post(
            "/api/v1/schedules",
            json={"project_id": project_id, "frequency": "daily"},
            headers=auth_headers,
        )

        response = await client.get(
            f"/api/v1/schedules/project/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id

    @pytest.mark.asyncio
    async def test_get_schedule_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test getting non-existent schedule."""
        response = await client.get(
            f"/api/v1/schedules/project/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_schedules(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test listing all schedules."""
        # Create projects with schedules
        for i in range(3):
            project_response = await client.post(
                "/api/v1/projects",
                json={"name": f"Project {i}", "preset": "standard"},
                headers=auth_headers,
            )
            pid = project_response.json()["id"]
            await client.post(
                "/api/v1/schedules",
                json={"project_id": pid, "frequency": "daily"},
                headers=auth_headers,
            )

        response = await client.get(
            "/api/v1/schedules",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_update_schedule(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test updating a schedule."""
        # Create schedule
        await client.post(
            "/api/v1/schedules",
            json={"project_id": project_id, "frequency": "daily", "time": "09:00"},
            headers=auth_headers,
        )

        # Update schedule
        response = await client.put(
            f"/api/v1/schedules/project/{project_id}",
            json={"frequency": "weekly", "day_of_week": 0, "time": "10:00"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "weekly"
        assert data["time"] == "10:00"

    @pytest.mark.asyncio
    async def test_toggle_schedule(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test toggling schedule enabled status."""
        # Create schedule
        create_response = await client.post(
            "/api/v1/schedules",
            json={"project_id": project_id, "frequency": "daily"},
            headers=auth_headers,
        )
        assert create_response.json()["enabled"] is True

        # Toggle off
        response = await client.post(
            f"/api/v1/schedules/project/{project_id}/toggle",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["enabled"] is False
        assert response.json()["next_run"] is None

        # Toggle on
        response = await client.post(
            f"/api/v1/schedules/project/{project_id}/toggle",
            headers=auth_headers,
        )

        assert response.json()["enabled"] is True
        assert response.json()["next_run"] is not None

    @pytest.mark.asyncio
    async def test_delete_schedule(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test deleting a schedule."""
        # Create schedule
        await client.post(
            "/api/v1/schedules",
            json={"project_id": project_id, "frequency": "daily"},
            headers=auth_headers,
        )

        # Delete schedule
        response = await client.delete(
            f"/api/v1/schedules/project/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(
            f"/api/v1/schedules/project/{project_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_time_format(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test schedule with invalid time format."""
        response = await client.post(
            "/api/v1/schedules",
            json={
                "project_id": project_id,
                "frequency": "daily",
                "time": "25:00",  # Invalid hour
            },
            headers=auth_headers,
        )

        assert response.status_code == 422
