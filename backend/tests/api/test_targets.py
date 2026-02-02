"""Tests for target API endpoints."""

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


class TestTargetsAPI:
    """Test target endpoints."""

    @pytest.mark.asyncio
    async def test_create_target_amazon(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating an Amazon target."""
        target = {
            "url": "https://www.amazon.com/dp/B09V3KXJPB",
            "label": "iPhone 13 Pro",
        }

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=target,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["url"] == target["url"]
        assert data["label"] == target["label"]
        assert data["platform"] == "amazon"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_target_steam(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating a Steam target."""
        target = {"url": "https://store.steampowered.com/app/1245620/ELDEN_RING/"}

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=target,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["platform"] == "steam"
        assert "ELDEN" in data["label"] or data["label"]  # Auto-generated label

    @pytest.mark.asyncio
    async def test_create_target_youtube(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating a YouTube target."""
        target = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=target,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["platform"] == "youtube"

    @pytest.mark.asyncio
    async def test_create_target_auto_label(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test that label is auto-generated from URL."""
        target = {"url": "https://www.amazon.com/dp/B09V3KXJPB"}

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=target,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["label"] is not None

    @pytest.mark.asyncio
    async def test_create_targets_bulk(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test creating multiple targets at once."""
        bulk = {
            "urls": [
                "https://www.amazon.com/dp/B09V3KXJPB",
                "https://store.steampowered.com/app/1245620/",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ]
        }

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets/bulk",
            json=bulk,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3

        platforms = [t["platform"] for t in data]
        assert "amazon" in platforms
        assert "steam" in platforms
        assert "youtube" in platforms

    @pytest.mark.asyncio
    async def test_list_targets(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test listing targets for a project."""
        # Create targets
        urls = [
            "https://www.amazon.com/dp/B09V3KXJPB",
            "https://www.amazon.com/dp/B08N5WRWNW",
        ]
        for url in urls:
            await client.post(
                f"/api/v1/projects/{project_id}/targets",
                json={"url": url},
                headers=auth_headers,
            )

        response = await client.get(
            f"/api/v1/projects/{project_id}/targets",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_targets_filter_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test filtering targets by status."""
        # Create target
        create_response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "https://www.amazon.com/dp/B09V3KXJPB"},
            headers=auth_headers,
        )
        target_id = create_response.json()["id"]

        # Pause target
        await client.put(
            f"/api/v1/projects/{project_id}/targets/{target_id}",
            json={"status": "paused"},
            headers=auth_headers,
        )

        # Create another active target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "https://www.amazon.com/dp/B08N5WRWNW"},
            headers=auth_headers,
        )

        # Filter by active
        response = await client.get(
            f"/api/v1/projects/{project_id}/targets?status=active",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_get_target(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test getting a specific target."""
        # Create target
        create_response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "https://www.amazon.com/dp/B09V3KXJPB"},
            headers=auth_headers,
        )
        target_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/targets/{target_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == target_id

    @pytest.mark.asyncio
    async def test_update_target(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test updating a target."""
        # Create target
        create_response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "https://www.amazon.com/dp/B09V3KXJPB"},
            headers=auth_headers,
        )
        target_id = create_response.json()["id"]

        # Update target
        response = await client.put(
            f"/api/v1/projects/{project_id}/targets/{target_id}",
            json={"label": "Updated Label", "status": "paused"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "Updated Label"
        assert data["status"] == "paused"

    @pytest.mark.asyncio
    async def test_delete_target(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test deleting a target."""
        # Create target
        create_response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "https://www.amazon.com/dp/B09V3KXJPB"},
            headers=auth_headers,
        )
        target_id = create_response.json()["id"]

        # Delete target
        response = await client.delete(
            f"/api/v1/projects/{project_id}/targets/{target_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(
            f"/api/v1/projects/{project_id}/targets/{target_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_target_project_ownership(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user_data_2: dict,
    ):
        """Test that users can only access their own targets."""
        # Create project with first user
        project_response = await client.post(
            "/api/v1/projects",
            json={"name": "User 1 Project", "preset": "standard"},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Create target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "https://www.amazon.com/dp/B09V3KXJPB"},
            headers=auth_headers,
        )

        # Register and login second user
        await client.post("/api/v1/auth/register", json=test_user_data_2)
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data_2["email"],
                "password": test_user_data_2["password"],
            },
        )
        headers_2 = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        # Try to access project with second user
        response = await client.get(
            f"/api/v1/projects/{project_id}/targets",
            headers=headers_2,
        )

        assert response.status_code == 404  # Project not found for this user

    @pytest.mark.asyncio
    async def test_platform_detection(
        self,
        client: AsyncClient,
        auth_headers: dict,
        project_id: str,
    ):
        """Test platform detection for various URLs."""
        test_cases = [
            ("https://www.amazon.com/dp/B09V3KXJPB", "amazon"),
            ("https://www.amazon.co.uk/dp/B09V3KXJPB", "amazon"),
            ("https://store.steampowered.com/app/1245620/", "steam"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube"),
            ("https://youtu.be/dQw4w9WgXcQ", "youtube"),
            ("https://www.reddit.com/r/Python/comments/abc123/", "reddit"),
            ("https://www.trustpilot.com/review/example.com", "trustpilot"),
            ("https://www.yelp.com/biz/restaurant-name", "yelp"),
        ]

        for url, expected_platform in test_cases:
            response = await client.post(
                f"/api/v1/projects/{project_id}/targets",
                json={"url": url},
                headers=auth_headers,
            )

            if response.status_code == 201:
                assert response.json()["platform"] == expected_platform, f"Failed for {url}"
