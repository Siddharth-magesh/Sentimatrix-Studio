"""Result repository for database operations."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.result import (
    Result,
    ResultAggregation,
    ResultFilter,
    ResultList,
)
from app.repositories.base import BaseRepository


class ResultRepository(BaseRepository):
    """Repository for result database operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "results")

    async def get_result(self, result_id: str, user_id: str) -> Result:
        """Get a result by ID."""
        result = await self.collection.find_one(
            {"_id": ObjectId(result_id), "user_id": user_id}
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result not found",
            )
        return self._doc_to_model(result, Result)

    async def get_results_by_project(
        self,
        project_id: str,
        user_id: str,
        filters: ResultFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ResultList:
        """Get paginated results for a project."""
        query: dict[str, Any] = {"project_id": project_id, "user_id": user_id}

        if filters:
            if filters.sentiment:
                query["analysis.sentiment.label"] = filters.sentiment
            if filters.platform:
                query["platform"] = filters.platform
            if filters.target_id:
                query["target_id"] = filters.target_id
            if filters.date_from:
                query["content.date"] = {"$gte": filters.date_from}
            if filters.date_to:
                if "content.date" in query:
                    query["content.date"]["$lte"] = filters.date_to
                else:
                    query["content.date"] = {"$lte": filters.date_to}
            if filters.search:
                query["$or"] = [
                    {"content.text": {"$regex": filters.search, "$options": "i"}},
                    {"content.title": {"$regex": filters.search, "$options": "i"}},
                ]

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)

        return ResultList(
            items=[self._doc_to_model(r, Result) for r in results],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_results_by_target(
        self,
        target_id: str,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> ResultList:
        """Get paginated results for a target."""
        query = {"target_id": target_id, "user_id": user_id}

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)

        return ResultList(
            items=[self._doc_to_model(r, Result) for r in results],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_results_by_job(
        self,
        job_id: str,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> ResultList:
        """Get paginated results for a scrape job."""
        query = {"scrape_job_id": job_id, "user_id": user_id}

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)

        return ResultList(
            items=[self._doc_to_model(r, Result) for r in results],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def delete_result(self, result_id: str, user_id: str) -> None:
        """Delete a result."""
        result = await self.collection.delete_one(
            {"_id": ObjectId(result_id), "user_id": user_id}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result not found",
            )

    async def delete_results_by_project(self, project_id: str, user_id: str) -> int:
        """Delete all results for a project."""
        result = await self.collection.delete_many(
            {"project_id": project_id, "user_id": user_id}
        )
        return result.deleted_count

    async def delete_results_by_target(self, target_id: str, user_id: str) -> int:
        """Delete all results for a target."""
        result = await self.collection.delete_many(
            {"target_id": target_id, "user_id": user_id}
        )
        return result.deleted_count

    async def get_aggregation(
        self,
        project_id: str,
        user_id: str,
        target_id: str | None = None,
    ) -> ResultAggregation:
        """Get aggregated statistics for results."""
        match_query: dict[str, Any] = {"project_id": project_id, "user_id": user_id}
        if target_id:
            match_query["target_id"] = target_id

        pipeline = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": None,
                    "total_results": {"$sum": 1},
                    "avg_sentiment_score": {"$avg": "$analysis.sentiment.score"},
                    "avg_rating": {"$avg": "$content.rating"},
                    "min_date": {"$min": "$content.date"},
                    "max_date": {"$max": "$content.date"},
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        agg_results = await cursor.to_list(length=1)

        if not agg_results:
            return ResultAggregation()

        agg = agg_results[0]

        # Get sentiment distribution
        sentiment_pipeline = [
            {"$match": match_query},
            {"$group": {"_id": "$analysis.sentiment.label", "count": {"$sum": 1}}},
        ]
        sentiment_cursor = self.collection.aggregate(sentiment_pipeline)
        sentiment_results = await sentiment_cursor.to_list(length=10)
        sentiment_dist = {
            s["_id"]: s["count"] for s in sentiment_results if s["_id"]
        }

        # Get platform distribution
        platform_pipeline = [
            {"$match": match_query},
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
        ]
        platform_cursor = self.collection.aggregate(platform_pipeline)
        platform_results = await platform_cursor.to_list(length=20)
        platform_dist = {
            p["_id"]: p["count"] for p in platform_results if p["_id"]
        }

        return ResultAggregation(
            total_results=agg.get("total_results", 0),
            sentiment_distribution=sentiment_dist,
            avg_sentiment_score=agg.get("avg_sentiment_score"),
            avg_rating=agg.get("avg_rating"),
            platforms=platform_dist,
            date_range={
                "earliest": agg.get("min_date"),
                "latest": agg.get("max_date"),
            },
        )

    async def get_sentiment_over_time(
        self,
        project_id: str,
        user_id: str,
        target_id: str | None = None,
        interval: str = "day",
    ) -> list[dict[str, Any]]:
        """Get sentiment score over time."""
        match_query: dict[str, Any] = {"project_id": project_id, "user_id": user_id}
        if target_id:
            match_query["target_id"] = target_id

        # Date truncation based on interval
        date_format = {
            "hour": "%Y-%m-%dT%H:00:00",
            "day": "%Y-%m-%d",
            "week": "%Y-W%V",
            "month": "%Y-%m",
        }.get(interval, "%Y-%m-%d")

        pipeline = [
            {"$match": match_query},
            {
                "$project": {
                    "date_bucket": {
                        "$dateToString": {"format": date_format, "date": "$content.date"}
                    },
                    "sentiment_score": "$analysis.sentiment.score",
                }
            },
            {
                "$group": {
                    "_id": "$date_bucket",
                    "avg_score": {"$avg": "$sentiment_score"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=1000)

        return [
            {"date": r["_id"], "avg_score": r["avg_score"], "count": r["count"]}
            for r in results
            if r["_id"]
        ]

    async def get_top_emotions(
        self,
        project_id: str,
        user_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get top detected emotions across all results."""
        match_query = {"project_id": project_id, "user_id": user_id}

        pipeline = [
            {"$match": match_query},
            {"$unwind": "$analysis.emotions.detected"},
            {
                "$group": {
                    "_id": "$analysis.emotions.detected.emotion",
                    "avg_score": {"$avg": "$analysis.emotions.detected.score"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]

        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)

        return [
            {"emotion": r["_id"], "avg_score": r["avg_score"], "count": r["count"]}
            for r in results
        ]

    async def export_results(
        self,
        project_id: str,
        user_id: str,
        format: str = "json",
    ) -> list[dict[str, Any]]:
        """Export all results for a project."""
        query = {"project_id": project_id, "user_id": user_id}

        cursor = self.collection.find(query).sort("created_at", -1)
        results = await cursor.to_list(length=None)

        export_data = []
        for r in results:
            r["id"] = str(r.pop("_id"))
            export_data.append(r)

        return export_data


def get_result_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ResultRepository:
    """Dependency for getting result repository."""
    return ResultRepository(db)
