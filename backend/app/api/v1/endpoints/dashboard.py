"""Dashboard endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.core.database import get_database
from app.core.deps import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService, DashboardStats, ProjectStats

router = APIRouter()


@router.get(
    "",
    response_model=DashboardStats,
    summary="Get dashboard stats",
)
async def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_database),
) -> DashboardStats:
    """
    Get overall dashboard statistics for the current user.

    Includes:
    - Project and target counts
    - Result counts and recent activity
    - Sentiment and platform distribution
    - Recent jobs and activity
    """
    service = DashboardService(db)
    return await service.get_dashboard_stats(current_user.id)


@router.get(
    "/projects/{project_id}",
    response_model=ProjectStats,
    summary="Get project stats",
)
async def get_project_stats(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_database),
) -> ProjectStats:
    """
    Get detailed statistics for a specific project.

    Includes:
    - Target and result counts
    - Last scrape time
    - Sentiment trend over time
    - Top detected emotions
    """
    service = DashboardService(db)
    return await service.get_project_stats(project_id, current_user.id)


@router.get(
    "/trends/{metric}",
    response_model=list[dict],
    summary="Get trend data",
)
async def get_trend_data(
    metric: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_database),
    interval: str = Query("day", description="Aggregation interval: hour, day, week, month"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
) -> list[dict[str, Any]]:
    """
    Get trend data for a specific metric.

    Available metrics:
    - **sentiment**: Average sentiment score over time
    - **volume**: Number of results over time
    """
    service = DashboardService(db)
    return await service.get_trend_data(
        user_id=current_user.id,
        metric=metric,
        interval=interval,
        days=days,
    )


@router.get(
    "/summary",
    response_model=dict,
    summary="Get quick summary",
)
async def get_quick_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_database),
) -> dict[str, Any]:
    """
    Get a quick summary of key metrics for the dashboard header.
    """
    from datetime import datetime, timezone, timedelta

    service = DashboardService(db)
    stats = await service.get_dashboard_stats(current_user.id)

    # Calculate changes (would need historical data for real implementation)
    return {
        "total_projects": stats.total_projects,
        "active_projects": stats.active_projects,
        "total_results": stats.total_results,
        "results_last_7_days": stats.results_last_7_days,
        "avg_sentiment": stats.avg_sentiment_score,
        "sentiment_label": _sentiment_label(stats.avg_sentiment_score),
        "top_platform": _get_top_key(stats.platform_distribution),
        "jobs_today": stats.jobs_last_24h,
    }


def _sentiment_label(score: float | None) -> str:
    """Convert sentiment score to label."""
    if score is None:
        return "unknown"
    if score > 0.3:
        return "positive"
    if score < -0.3:
        return "negative"
    return "neutral"


def _get_top_key(d: dict[str, int]) -> str | None:
    """Get the key with highest value."""
    if not d:
        return None
    return max(d.keys(), key=lambda k: d[k])
