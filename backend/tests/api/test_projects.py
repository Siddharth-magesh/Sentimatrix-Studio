"""Tests for project API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user_data: dict) -> dict:
    """Get auth headers for authenticated requests."""
    # Register user
    await client.post("/api/v1/auth/register", json=test_user_data)

    # Login to get token
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
def sample_project() -> dict:
    """Sample project data."""
    return {
        "name": "Test Project",
        "description": "A test project for sentiment analysis",
        "preset": "standard",
    }


class TestProjectsAPI:
    """Test project endpoints."""

    @pytest.mark.asyncio
    async def test_create_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test creating a new project."""
        response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project["name"]
        assert data["description"] == sample_project["description"]
        assert data["preset"] == sample_project["preset"]
        assert data["status"] == "active"
        assert "id" in data
        assert "config" in data
        assert "stats" in data

    @pytest.mark.asyncio
    async def test_create_project_custom_config(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test creating a project with custom config."""
        project = {
            "name": "Custom Project",
            "preset": "custom",
            "config": {
                "scrapers": {
                    "platforms": ["amazon", "steam"],
                    "commercial_provider": None,
                },
                "llm": {
                    "provider": "groq",
                    "model": "llama-3.3-70b-versatile",
                    "temperature": 0.5,
                    "max_tokens": 1000,
                },
                "analysis": {
                    "sentiment": True,
                    "sentiment_classes": 5,
                    "emotions": True,
                    "emotion_model": "goemotions",
                    "summarize": False,
                    "extract_insights": False,
                },
                "limits": {
                    "max_reviews_per_target": 100,
                    "max_requests_per_day": 500,
                    "rate_limit_delay": 1.0,
                },
            },
        }

        response = await client.post(
            "/api/v1/projects",
            json=project,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["preset"] == "custom"
        assert data["config"]["scrapers"]["platforms"] == ["amazon", "steam"]
        assert data["config"]["analysis"]["sentiment_classes"] == 5

    @pytest.mark.asyncio
    async def test_create_project_unauthorized(
        self,
        client: AsyncClient,
        sample_project: dict,
    ):
        """Test creating project without authentication."""
        response = await client.post("/api/v1/projects", json=sample_project)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_projects(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test listing projects."""
        # Create multiple projects
        for i in range(3):
            project = {**sample_project, "name": f"Project {i}"}
            await client.post("/api/v1/projects", json=project, headers=auth_headers)

        response = await client.get("/api/v1/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_list_projects_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test project list pagination."""
        # Create 5 projects
        for i in range(5):
            project = {**sample_project, "name": f"Project {i}"}
            await client.post("/api/v1/projects", json=project, headers=auth_headers)

        # Get first page
        response = await client.get(
            "/api/v1/projects?page=1&page_size=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1

        # Get second page
        response = await client.get(
            "/api/v1/projects?page=2&page_size=2",
            headers=auth_headers,
        )

        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 2

    @pytest.mark.asyncio
    async def test_get_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test getting a specific project."""
        # Create project
        create_response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # Get project
        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == sample_project["name"]

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting non-existent project."""
        response = await client.get(
            "/api/v1/projects/000000000000000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test updating a project."""
        # Create project
        create_response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # Update project
        update_data = {
            "name": "Updated Project",
            "description": "Updated description",
        }
        response = await client.put(
            f"/api/v1/projects/{project_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_project_soft(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test soft deleting a project."""
        # Create project
        create_response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # Soft delete
        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Project should be archived
        get_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )
        assert get_response.json()["status"] == "archived"

    @pytest.mark.asyncio
    async def test_delete_project_permanent(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test permanently deleting a project."""
        # Create project
        create_response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # Hard delete
        response = await client.delete(
            f"/api/v1/projects/{project_id}?permanent=true",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Project should not exist
        get_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_stats(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_project: dict,
    ):
        """Test getting project statistics."""
        # Create project
        create_response = await client.post(
            "/api/v1/projects",
            json=sample_project,
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # Get stats
        response = await client.get(
            f"/api/v1/projects/{project_id}/stats",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_targets" in data
        assert "total_results" in data
        assert "scrape_jobs_completed" in data

    @pytest.mark.asyncio
    async def test_project_search(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test searching projects by name."""
        # Create projects
        await client.post(
            "/api/v1/projects",
            json={"name": "Amazon Analysis", "preset": "standard"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/projects",
            json={"name": "Steam Reviews", "preset": "standard"},
            headers=auth_headers,
        )

        # Search
        response = await client.get(
            "/api/v1/projects?search=amazon",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Amazon" in data["items"][0]["name"]
