"""Health check endpoints."""

import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Response, status

from app import __version__
from app.core.config import get_settings
from app.db.mongodb import MongoDB

router = APIRouter()

# Track application start time
_start_time = time.time()


async def check_redis() -> dict[str, Any]:
    """Check Redis connectivity."""
    try:
        from app.core.cache import cache

        if cache is None:
            return {"healthy": False, "error": "Cache not initialized"}

        # Test set/get
        test_key = "_health_check_"
        await cache.set(test_key, "ok", ttl=10)
        result = await cache.get(test_key)

        if result == "ok":
            return {"healthy": True, "latency_ms": 0}
        return {"healthy": False, "error": "Get/Set mismatch"}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Check application health.

    Returns basic health status and version information.
    Used by load balancers and monitoring systems.
    """
    settings = get_settings()
    uptime_seconds = int(time.time() - _start_time)

    return {
        "status": "healthy",
        "version": __version__,
        "environment": settings.app_env,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime_seconds,
    }


@router.get("/health/ready")
async def readiness_check(response: Response) -> dict[str, Any]:
    """
    Check if the application is ready to serve requests.

    Verifies database and cache connectivity.
    Used by Kubernetes readiness probes.
    """
    settings = get_settings()

    # Check all dependencies
    db_health = await MongoDB.health_check()
    redis_health = await check_redis()

    # Determine overall status
    is_db_healthy = db_health.get("healthy", False)
    is_redis_healthy = redis_health.get("healthy", False)
    is_ready = is_db_healthy and is_redis_healthy

    # Set appropriate status code
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "version": __version__,
        "environment": settings.app_env,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": {
                "status": "up" if is_db_healthy else "down",
                **db_health,
            },
            "redis": {
                "status": "up" if is_redis_healthy else "down",
                **redis_health,
            },
        },
    }


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """
    Check if the application is alive.

    Simple endpoint for Kubernetes liveness probes.
    Returns immediately without checking dependencies.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/details")
async def detailed_health_check(response: Response) -> dict[str, Any]:
    """
    Get detailed health information.

    Returns comprehensive system information including
    memory usage, connections, and dependency status.
    """
    import os
    import platform
    import sys

    settings = get_settings()
    db_health = await MongoDB.health_check()
    redis_health = await check_redis()

    is_db_healthy = db_health.get("healthy", False)
    is_redis_healthy = redis_health.get("healthy", False)
    is_healthy = is_db_healthy and is_redis_healthy

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "version": __version__,
        "environment": settings.app_env,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _start_time),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "pid": os.getpid(),
        },
        "checks": {
            "database": {
                "status": "up" if is_db_healthy else "down",
                **db_health,
            },
            "redis": {
                "status": "up" if is_redis_healthy else "down",
                **redis_health,
            },
        },
    }
