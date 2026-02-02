"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1 import router as v1_router
from app.core.config import get_settings
from app.core.error_handler import register_exception_handlers
from app.core.logging import setup_logging
from app.db.mongodb import MongoDB
from app.middleware import RequestIDMiddleware

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    setup_logging()
    logger.info("Starting Sentimatrix Studio", version=__version__)

    await MongoDB.connect()

    yield

    # Shutdown
    logger.info("Shutting down Sentimatrix Studio")
    await MongoDB.disconnect()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="No-code web platform for sentiment analysis powered by Sentimatrix",
        version=__version__,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Include API routers
    app.include_router(v1_router, prefix="/api")

    return app


app = create_app()


def run() -> None:
    """Run the application using uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )


if __name__ == "__main__":
    run()
