"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import Settings, get_settings
from app.db.mongodb import MongoDB
from app.main import create_app


def get_test_settings() -> Settings:
    """Get test settings with test database."""
    return Settings(
        mongodb_db_name="sentimatrix_studio_test",
        jwt_secret_key="test-secret-key",
        secret_key="test-secret-key",
        debug=True,
        app_env="development",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[None, None]:
    """Set up and tear down test database."""
    settings = get_test_settings()

    # Override settings
    from app.core import config
    config.get_settings = lambda: settings

    # Connect to test database
    await MongoDB.connect()

    yield

    # Clean up test database
    db = MongoDB.get_database()
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})

    await MongoDB.disconnect()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: None) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(scope="function")
def sync_client(test_db: None) -> Generator[TestClient, None, None]:
    """Create sync test client."""
    app = create_app()
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def test_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "TestPass123",
    }


@pytest.fixture
def test_user_data_2() -> dict:
    """Second sample user data for testing."""
    return {
        "email": "test2@example.com",
        "name": "Test User 2",
        "password": "TestPass456",
    }
