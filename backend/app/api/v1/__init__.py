"""API v1 module."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    oauth,
    projects,
    targets,
    scrape,
    results,
    settings,
    schedules,
    webhooks,
    dashboard,
    websocket,
)

router = APIRouter(prefix="/v1")

# Health check
router.include_router(health.router, tags=["health"])

# Authentication
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])

# Projects and related resources
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(targets.router, prefix="/projects", tags=["targets"])
router.include_router(scrape.router, prefix="/projects", tags=["scrape"])
router.include_router(results.router, prefix="/projects", tags=["results"])

# Settings and configuration
router.include_router(settings.router, prefix="/settings", tags=["settings"])

# Scheduling
router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])

# Webhooks
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Dashboard
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# WebSocket
router.include_router(websocket.router, tags=["websocket"])
