"""Health check endpoints."""

from typing import Any

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.db.mongodb import MongoDB

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Check application health.

    Returns basic health status and version information.
    """
    settings = get_settings()

    return {
        "status": "healthy",
        "version": __version__,
        "environment": settings.app_env,
    }


@router.get("/health/ready")
async def readiness_check() -> dict[str, Any]:
    """
    Check if the application is ready to serve requests.

    Verifies database connectivity and returns detailed status.
    """
    settings = get_settings()
    db_health = await MongoDB.health_check()

    is_ready = db_health.get("healthy", False)

    return {
        "status": "ready" if is_ready else "not_ready",
        "version": __version__,
        "environment": settings.app_env,
        "checks": {
            "database": db_health,
        },
    }


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """
    Check if the application is alive.

    Simple endpoint for Kubernetes liveness probes.
    """
    return {"status": "alive"}
