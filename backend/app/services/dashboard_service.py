"""Dashboard statistics service."""

from datetime import datetime, timezone, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.base import StudioBaseModel


class DashboardStats(StudioBaseModel):
    """Overall dashboard statistics."""

    total_projects: int = 0
    active_projects: int = 0
    total_targets: int = 0
    total_results: int = 0
    total_scrape_jobs: int = 0
    jobs_last_24h: int = 0
    results_last_7_days: int = 0
    avg_sentiment_score: float | None = None
    sentiment_distribution: dict[str, int] = {}
    platform_distribution: dict[str, int] = {}
    recent_jobs: list[dict] = []
    recent_activity: list[dict] = []


class ProjectStats(StudioBaseModel):
    """Statistics for a single project."""

    project_id: str
    project_name: str
    total_targets: int = 0
    active_targets: int = 0
    total_results: int = 0
    total_jobs: int = 0
    last_scrape: datetime | None = None
    avg_sentiment_score: float | None = None
    sentiment_trend: list[dict] = []
    top_emotions: list[dict] = []


class DashboardService:
    """Service for aggregating dashboard statistics."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.projects = db["projects"]
        self.targets = db["targets"]
        self.results = db["results"]
        self.scrape_jobs = db["scrape_jobs"]

    async def get_dashboard_stats(self, user_id: str) -> DashboardStats:
        """Get overall dashboard statistics for a user."""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_7_days = now - timedelta(days=7)

        # Project counts
        total_projects = await self.projects.count_documents({"user_id": user_id})
        active_projects = await self.projects.count_documents(
            {"user_id": user_id, "status": "active"}
        )

        # Target count
        total_targets = await self.targets.count_documents({"user_id": user_id})

        # Result count
        total_results = await self.results.count_documents({"user_id": user_id})
        results_last_7_days = await self.results.count_documents(
            {"user_id": user_id, "created_at": {"$gte": last_7_days}}
        )

        # Job counts
        total_jobs = await self.scrape_jobs.count_documents({"user_id": user_id})
        jobs_last_24h = await self.scrape_jobs.count_documents(
            {"user_id": user_id, "created_at": {"$gte": last_24h}}
        )

        # Average sentiment
        sentiment_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$analysis.sentiment.score"}}},
        ]
        sentiment_result = await self.results.aggregate(sentiment_pipeline).to_list(1)
        avg_sentiment = sentiment_result[0]["avg_score"] if sentiment_result else None

        # Sentiment distribution
        sentiment_dist_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$analysis.sentiment.label", "count": {"$sum": 1}}},
        ]
        sentiment_dist_result = await self.results.aggregate(sentiment_dist_pipeline).to_list(10)
        sentiment_distribution = {
            r["_id"]: r["count"] for r in sentiment_dist_result if r["_id"]
        }

        # Platform distribution
        platform_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
        ]
        platform_result = await self.results.aggregate(platform_pipeline).to_list(20)
        platform_distribution = {
            r["_id"]: r["count"] for r in platform_result if r["_id"]
        }

        # Recent jobs
        recent_jobs_cursor = (
            self.scrape_jobs.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(5)
        )
        recent_jobs_docs = await recent_jobs_cursor.to_list(5)
        recent_jobs = [
            {
                "id": str(j["_id"]),
                "project_id": j["project_id"],
                "status": j["status"],
                "progress": j.get("progress", 0),
                "created_at": j["created_at"],
            }
            for j in recent_jobs_docs
        ]

        # Recent activity (combined jobs and results)
        recent_activity = await self._get_recent_activity(user_id, limit=10)

        return DashboardStats(
            total_projects=total_projects,
            active_projects=active_projects,
            total_targets=total_targets,
            total_results=total_results,
            total_scrape_jobs=total_jobs,
            jobs_last_24h=jobs_last_24h,
            results_last_7_days=results_last_7_days,
            avg_sentiment_score=avg_sentiment,
            sentiment_distribution=sentiment_distribution,
            platform_distribution=platform_distribution,
            recent_jobs=recent_jobs,
            recent_activity=recent_activity,
        )

    async def get_project_stats(
        self,
        project_id: str,
        user_id: str,
    ) -> ProjectStats:
        """Get detailed statistics for a specific project."""
        # Get project
        project = await self.projects.find_one(
            {"_id": project_id, "user_id": user_id}
        )
        project_name = project["name"] if project else "Unknown"

        # Target counts
        total_targets = await self.targets.count_documents(
            {"project_id": project_id, "user_id": user_id}
        )
        active_targets = await self.targets.count_documents(
            {"project_id": project_id, "user_id": user_id, "status": "active"}
        )

        # Result count
        total_results = await self.results.count_documents(
            {"project_id": project_id, "user_id": user_id}
        )

        # Job count
        total_jobs = await self.scrape_jobs.count_documents(
            {"project_id": project_id, "user_id": user_id}
        )

        # Last scrape
        last_job = await self.scrape_jobs.find_one(
            {"project_id": project_id, "user_id": user_id, "status": "completed"},
            sort=[("completed_at", -1)],
        )
        last_scrape = last_job.get("completed_at") if last_job else None

        # Average sentiment
        sentiment_pipeline = [
            {"$match": {"project_id": project_id, "user_id": user_id}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$analysis.sentiment.score"}}},
        ]
        sentiment_result = await self.results.aggregate(sentiment_pipeline).to_list(1)
        avg_sentiment = sentiment_result[0]["avg_score"] if sentiment_result else None

        # Sentiment trend (last 30 days)
        sentiment_trend = await self._get_sentiment_trend(project_id, user_id, days=30)

        # Top emotions
        top_emotions = await self._get_top_emotions(project_id, user_id, limit=5)

        return ProjectStats(
            project_id=project_id,
            project_name=project_name,
            total_targets=total_targets,
            active_targets=active_targets,
            total_results=total_results,
            total_jobs=total_jobs,
            last_scrape=last_scrape,
            avg_sentiment_score=avg_sentiment,
            sentiment_trend=sentiment_trend,
            top_emotions=top_emotions,
        )

    async def _get_recent_activity(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get recent activity combining jobs and results."""
        activity = []

        # Get recent jobs
        jobs_cursor = (
            self.scrape_jobs.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        async for job in jobs_cursor:
            activity.append({
                "type": "job",
                "id": str(job["_id"]),
                "status": job["status"],
                "timestamp": job["created_at"],
                "description": f"Scrape job {job['status']}",
            })

        # Sort by timestamp and limit
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        return activity[:limit]

    async def _get_sentiment_trend(
        self,
        project_id: str,
        user_id: str,
        days: int = 30,
    ) -> list[dict]:
        """Get sentiment score trend over time."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        pipeline = [
            {"$match": {
                "project_id": project_id,
                "user_id": user_id,
                "created_at": {"$gte": cutoff},
            }},
            {"$project": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "score": "$analysis.sentiment.score",
            }},
            {"$group": {
                "_id": "$date",
                "avg_score": {"$avg": "$score"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ]

        result = await self.results.aggregate(pipeline).to_list(days)
        return [
            {"date": r["_id"], "avg_score": r["avg_score"], "count": r["count"]}
            for r in result
        ]

    async def _get_top_emotions(
        self,
        project_id: str,
        user_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """Get top detected emotions."""
        pipeline = [
            {"$match": {"project_id": project_id, "user_id": user_id}},
            {"$unwind": "$analysis.emotions.detected"},
            {"$group": {
                "_id": "$analysis.emotions.detected.emotion",
                "avg_score": {"$avg": "$analysis.emotions.detected.score"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]

        result = await self.results.aggregate(pipeline).to_list(limit)
        return [
            {"emotion": r["_id"], "avg_score": r["avg_score"], "count": r["count"]}
            for r in result
        ]

    async def get_trend_data(
        self,
        user_id: str,
        metric: str = "sentiment",
        interval: str = "day",
        days: int = 30,
    ) -> list[dict]:
        """Get trend data for a specific metric."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        date_format = {
            "hour": "%Y-%m-%dT%H:00",
            "day": "%Y-%m-%d",
            "week": "%Y-W%V",
            "month": "%Y-%m",
        }.get(interval, "%Y-%m-%d")

        if metric == "sentiment":
            pipeline = [
                {"$match": {"user_id": user_id, "created_at": {"$gte": cutoff}}},
                {"$project": {
                    "bucket": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                    "score": "$analysis.sentiment.score",
                }},
                {"$group": {
                    "_id": "$bucket",
                    "value": {"$avg": "$score"},
                    "count": {"$sum": 1},
                }},
                {"$sort": {"_id": 1}},
            ]
        elif metric == "volume":
            pipeline = [
                {"$match": {"user_id": user_id, "created_at": {"$gte": cutoff}}},
                {"$project": {
                    "bucket": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                }},
                {"$group": {
                    "_id": "$bucket",
                    "value": {"$sum": 1},
                }},
                {"$sort": {"_id": 1}},
            ]
        else:
            return []

        result = await self.results.aggregate(pipeline).to_list(days * 24)
        return [
            {"date": r["_id"], "value": r["value"], "count": r.get("count", r["value"])}
            for r in result
        ]
