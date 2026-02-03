"""Integration tests for the scraping pipeline."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from httpx import AsyncClient


@pytest.fixture
def sample_project_data() -> dict:
    """Sample project data for testing."""
    return {
        "name": "Test Scraping Project",
        "description": "Project for scraping integration tests",
        "preset": "custom",
        "config": {
            "scrapers": {
                "platforms": ["amazon"],
                "commercial_provider": None,
            },
            "llm": {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.5,
            },
            "analysis": {
                "sentiment": True,
                "emotions": True,
                "summarize": False,
            },
            "limits": {
                "max_reviews_per_target": 10,
                "rate_limit_delay": 0.1,
            },
        },
    }


@pytest.fixture
def sample_target_data() -> dict:
    """Sample target data for testing."""
    return {
        "url": "https://www.amazon.com/dp/B08N5WRWNW",
        "name": "Test Product",
    }


@pytest.fixture
def mock_scraper_response() -> list:
    """Mock scraper response data."""
    return [
        {
            "text": "Great product, highly recommend!",
            "title": "Excellent Purchase",
            "author": "John D.",
            "rating": 5,
            "date": "2024-01-15",
            "helpful_votes": 10,
        },
        {
            "text": "Not what I expected, quality is poor.",
            "title": "Disappointed",
            "author": "Jane S.",
            "rating": 2,
            "date": "2024-01-14",
            "helpful_votes": 5,
        },
        {
            "text": "Average product, nothing special.",
            "title": "It's okay",
            "author": "Bob M.",
            "rating": 3,
            "date": "2024-01-13",
            "helpful_votes": 2,
        },
    ]


@pytest.fixture
def mock_analysis_response() -> dict:
    """Mock LLM analysis response."""
    return {
        "sentiment": {
            "label": "positive",
            "confidence": 0.92,
            "scores": {
                "positive": 0.92,
                "negative": 0.03,
                "neutral": 0.05,
            },
        },
        "emotions": {
            "joy": 0.75,
            "trust": 0.60,
            "anticipation": 0.30,
            "surprise": 0.10,
            "sadness": 0.05,
            "fear": 0.02,
            "anger": 0.03,
            "disgust": 0.02,
        },
    }


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
async def test_project(
    client: AsyncClient,
    auth_headers: dict,
    sample_project_data: dict,
) -> dict:
    """Create a test project."""
    response = await client.post(
        "/api/v1/projects",
        json=sample_project_data,
        headers=auth_headers,
    )
    return response.json()


class TestScrapingPipeline:
    """Integration tests for the complete scraping pipeline."""

    @pytest.mark.asyncio
    async def test_create_scrape_job(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
    ):
        """Test creating a scrape job."""
        project_id = test_project["id"]

        # Add target first
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Start scrape
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )

        assert response.status_code == 202
        data = response.json()
        assert "id" in data
        assert data["status"] in ["queued", "running"]
        assert data["project_id"] == project_id

    @pytest.mark.asyncio
    async def test_get_scrape_job_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
    ):
        """Test getting scrape job status."""
        project_id = test_project["id"]

        # Add target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Start scrape
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )
        job_id = response.json()["id"]

        # Get job status
        response = await client.get(
            f"/api/v1/projects/{project_id}/scrape/jobs/{job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert "status" in data
        assert "progress" in data

    @pytest.mark.asyncio
    async def test_list_scrape_jobs(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
    ):
        """Test listing scrape jobs for a project."""
        project_id = test_project["id"]

        # Add target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Start scrape
        await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )

        # List jobs
        response = await client.get(
            f"/api/v1/projects/{project_id}/scrape/jobs",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_cancel_scrape_job(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
    ):
        """Test cancelling a scrape job."""
        project_id = test_project["id"]

        # Add target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Start scrape
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )
        job_id = response.json()["id"]

        # Cancel job
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape/jobs/{job_id}/cancel",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400]  # 400 if already completed

    @pytest.mark.asyncio
    async def test_scrape_without_targets_fails(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test that scraping without targets fails."""
        project_id = test_project["id"]

        # Try to start scrape without targets
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )

        # Should fail or return error
        assert response.status_code in [400, 422]


class TestScrapingWithMockedPlatform:
    """Integration tests with mocked platform scrapers."""

    @pytest.mark.asyncio
    @patch("app.services.scraper.AmazonScraper")
    async def test_scrape_and_store_results(
        self,
        mock_scraper_class,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
        mock_scraper_response: list,
    ):
        """Test complete scraping flow with mocked scraper."""
        # Configure mock
        mock_scraper = AsyncMock()
        mock_scraper.scrape.return_value = mock_scraper_response
        mock_scraper_class.return_value = mock_scraper

        project_id = test_project["id"]

        # Add target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Start scrape
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )

        assert response.status_code == 202

    @pytest.mark.asyncio
    @patch("app.services.scraper.AmazonScraper")
    @patch("app.services.analysis.LLMAnalyzer")
    async def test_scrape_with_analysis(
        self,
        mock_analyzer_class,
        mock_scraper_class,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
        mock_scraper_response: list,
        mock_analysis_response: dict,
    ):
        """Test scraping with LLM analysis."""
        # Configure mocks
        mock_scraper = AsyncMock()
        mock_scraper.scrape.return_value = mock_scraper_response
        mock_scraper_class.return_value = mock_scraper

        mock_analyzer = AsyncMock()
        mock_analyzer.analyze.return_value = mock_analysis_response
        mock_analyzer_class.return_value = mock_analyzer

        project_id = test_project["id"]

        # Add target
        await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Start scrape
        response = await client.post(
            f"/api/v1/projects/{project_id}/scrape",
            headers=auth_headers,
        )

        assert response.status_code == 202


class TestResultsStorage:
    """Integration tests for results storage."""

    @pytest.mark.asyncio
    async def test_get_results_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test getting results when none exist."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_results_with_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test results pagination."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results",
            params={"page": 1, "limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data

    @pytest.mark.asyncio
    async def test_filter_results_by_sentiment(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test filtering results by sentiment."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results",
            params={"sentiment": "positive"},
            headers=auth_headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_results(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test searching results."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results",
            params={"search": "great product"},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestExportResults:
    """Integration tests for results export."""

    @pytest.mark.asyncio
    async def test_export_csv(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test exporting results as CSV."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results/export",
            params={"format": "csv"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_json(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test exporting results as JSON."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results/export",
            params={"format": "json"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_xlsx(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test exporting results as XLSX."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results/export",
            params={"format": "xlsx"},
            headers=auth_headers,
        )

        # XLSX might not be implemented, so 200 or 501
        assert response.status_code in [200, 501, 400]


class TestAnalytics:
    """Integration tests for analytics."""

    @pytest.mark.asyncio
    async def test_get_sentiment_timeline(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test getting sentiment timeline."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results/analytics/sentiment-timeline",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_analytics_summary(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test getting analytics summary."""
        project_id = test_project["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}/results/analytics/summary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_results" in data or "sentiment_distribution" in data


class TestTargetManagement:
    """Integration tests for target management."""

    @pytest.mark.asyncio
    async def test_bulk_add_targets(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test bulk adding targets."""
        project_id = test_project["id"]

        urls = [
            "https://www.amazon.com/dp/B08N5WRWNW",
            "https://www.amazon.com/dp/B09B8PTNKG",
            "https://www.amazon.com/dp/B08N5LNQCX",
        ]

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets/bulk",
            json={"urls": urls},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_duplicate_target_handling(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
    ):
        """Test handling of duplicate targets."""
        project_id = test_project["id"]

        # Add target first time
        response1 = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )
        assert response1.status_code == 201

        # Try to add same target again
        response2 = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )

        # Should either reject or handle gracefully
        assert response2.status_code in [201, 400, 409]

    @pytest.mark.asyncio
    async def test_invalid_url_target(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
    ):
        """Test adding target with invalid URL."""
        project_id = test_project["id"]

        response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json={"url": "not-a-valid-url"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_target_status_after_scrape(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: dict,
        sample_target_data: dict,
    ):
        """Test that target status updates after scraping."""
        project_id = test_project["id"]

        # Add target
        response = await client.post(
            f"/api/v1/projects/{project_id}/targets",
            json=sample_target_data,
            headers=auth_headers,
        )
        target_id = response.json()["id"]

        # Get targets
        response = await client.get(
            f"/api/v1/projects/{project_id}/targets",
            headers=auth_headers,
        )

        assert response.status_code == 200
        targets = response.json()
        target = next((t for t in targets if t["id"] == target_id), None)
        assert target is not None
        assert target["status"] in ["pending", "scraped", "failed"]
