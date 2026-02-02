"""Pydantic models for the application."""

from app.models.user import User, UserCreate, UserUpdate, UserInDB
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectInDB,
    ProjectList,
    ProjectConfig,
    ProjectStats,
)
from app.models.target import (
    Target,
    TargetCreate,
    TargetBulkCreate,
    TargetUpdate,
    TargetInDB,
    TargetList,
)
from app.models.scrape_job import (
    ScrapeJob,
    ScrapeJobCreate,
    ScrapeJobInDB,
    ScrapeJobList,
)
from app.models.result import (
    Result,
    ResultInDB,
    ResultList,
    ResultFilter,
    ResultAggregation,
)

__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    # Project
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectInDB",
    "ProjectList",
    "ProjectConfig",
    "ProjectStats",
    # Target
    "Target",
    "TargetCreate",
    "TargetBulkCreate",
    "TargetUpdate",
    "TargetInDB",
    "TargetList",
    # ScrapeJob
    "ScrapeJob",
    "ScrapeJobCreate",
    "ScrapeJobInDB",
    "ScrapeJobList",
    # Result
    "Result",
    "ResultInDB",
    "ResultList",
    "ResultFilter",
    "ResultAggregation",
]
