"""MongoDB connection manager with connection pooling."""

from typing import Any

import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class MongoDB:
    """MongoDB connection manager with connection pooling and lifecycle management."""

    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls) -> None:
        """Establish MongoDB connection with connection pooling."""
        settings = get_settings()

        if cls._client is not None:
            logger.info("MongoDB already connected")
            return

        logger.info(
            "Connecting to MongoDB",
            url=settings.mongodb_url.split("@")[-1] if "@" in settings.mongodb_url else "localhost",
            database=settings.mongodb_db_name,
        )

        try:
            cls._client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )

            # Verify connection
            await cls._client.admin.command("ping")

            cls._database = cls._client[settings.mongodb_db_name]

            logger.info("MongoDB connection established successfully")

            # Initialize indexes
            await cls._create_indexes()

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            cls._client = None
            cls._database = None
            raise

    @classmethod
    async def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls._client is not None:
            logger.info("Closing MongoDB connection")
            cls._client.close()
            cls._client = None
            cls._database = None
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if cls._database is None:
            raise RuntimeError("MongoDB is not connected. Call MongoDB.connect() first.")
        return cls._database

    @classmethod
    def get_collection(cls, name: str) -> Any:
        """Get a collection from the database."""
        return cls.get_database()[name]

    @classmethod
    async def _create_indexes(cls) -> None:
        """Create database indexes for all collections."""
        if cls._database is None:
            return

        logger.info("Creating database indexes")

        # Users collection indexes
        users = cls._database["users"]
        await users.create_index("email", unique=True)
        await users.create_index("created_at")

        # Projects collection indexes
        projects = cls._database["projects"]
        await projects.create_index("user_id")
        await projects.create_index("status")
        await projects.create_index([("user_id", 1), ("created_at", -1)])

        # Targets collection indexes
        targets = cls._database["targets"]
        await targets.create_index("project_id")
        await targets.create_index([("project_id", 1), ("platform", 1)])

        # Results collection indexes
        results = cls._database["results"]
        await results.create_index("project_id")
        await results.create_index("target_id")
        await results.create_index("sentiment")
        await results.create_index([("project_id", 1), ("created_at", -1)])

        # Scrape jobs collection indexes
        scrape_jobs = cls._database["scrape_jobs"]
        await scrape_jobs.create_index("project_id")
        await scrape_jobs.create_index("status")
        await scrape_jobs.create_index([("project_id", 1), ("created_at", -1)])

        # API keys collection indexes
        api_keys = cls._database["api_keys"]
        await api_keys.create_index("user_id")
        await api_keys.create_index("key_hash", unique=True)

        # Refresh tokens collection indexes
        refresh_tokens = cls._database["refresh_tokens"]
        await refresh_tokens.create_index("user_id")
        await refresh_tokens.create_index("token_hash", unique=True)
        await refresh_tokens.create_index("expires_at", expireAfterSeconds=0)

        logger.info("Database indexes created successfully")

    @classmethod
    async def health_check(cls) -> dict[str, Any]:
        """Check MongoDB connection health."""
        if cls._client is None:
            return {"status": "disconnected", "healthy": False}

        try:
            await cls._client.admin.command("ping")
            return {
                "status": "connected",
                "healthy": True,
                "database": get_settings().mongodb_db_name,
            }
        except Exception as e:
            return {"status": "error", "healthy": False, "error": str(e)}


async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get the database instance."""
    return MongoDB.get_database()
