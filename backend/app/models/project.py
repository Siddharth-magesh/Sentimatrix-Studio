"""Project model definitions."""

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


# Nested configuration models
class ScraperCommercialConfig(StudioBaseModel):
    """Commercial scraper configuration."""

    api_key_id: str | None = None
    render_js: bool = False
    country: str | None = None
    premium_proxy: bool = False


class ScraperConfig(StudioBaseModel):
    """Scraper configuration."""

    platforms: list[str] = Field(default_factory=list)
    commercial_provider: Literal["scraperapi", "apify", "scrapingbee"] | None = None
    commercial_config: ScraperCommercialConfig | None = None

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v: list[str]) -> list[str]:
        valid_platforms = {"amazon", "steam", "youtube", "reddit", "google", "trustpilot", "yelp"}
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")
        return [p.lower() for p in v]


class LLMConfig(StudioBaseModel):
    """LLM configuration."""

    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"
    api_key_id: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=100, le=8000)


class AnalysisConfig(StudioBaseModel):
    """Analysis configuration."""

    sentiment: bool = True
    sentiment_classes: Literal[3, 5] = 3
    emotions: bool = False
    emotion_model: Literal["ekman", "goemotions", "plutchik"] = "ekman"
    summarize: bool = False
    extract_insights: bool = False


class ScheduleConfig(StudioBaseModel):
    """Schedule configuration."""

    enabled: bool = False
    frequency: Literal["hourly", "daily", "weekly"] = "daily"
    time: str = "00:00"
    timezone: str = "UTC"
    days: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])  # Mon-Fri
    next_run_at: datetime | None = None

    @field_validator("days")
    @classmethod
    def validate_days(cls, v: list[int]) -> list[int]:
        for day in v:
            if day < 0 or day > 6:
                raise ValueError("Days must be 0-6 (Sunday-Saturday)")
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v


class LimitsConfig(StudioBaseModel):
    """Limits configuration."""

    max_reviews_per_target: int = Field(default=100, ge=10, le=1000)
    max_requests_per_day: int = Field(default=500, ge=10, le=10000)
    rate_limit_delay: float = Field(default=1.0, ge=0.1, le=10.0)


class ProjectConfig(StudioBaseModel):
    """Complete project configuration."""

    scrapers: ScraperConfig = Field(default_factory=ScraperConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)


class SentimentDistribution(StudioBaseModel):
    """Sentiment distribution stats."""

    positive: int = 0
    neutral: int = 0
    negative: int = 0


class ProjectStats(StudioBaseModel):
    """Project statistics."""

    total_targets: int = 0
    total_results: int = 0
    total_scrapes: int = 0
    avg_sentiment: float | None = None
    sentiment_distribution: SentimentDistribution = Field(default_factory=SentimentDistribution)
    last_scrape_at: datetime | None = None
    last_analysis_at: datetime | None = None


# Main models
class ProjectBase(StudioBaseModel):
    """Base project model."""

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)


class ProjectCreate(ProjectBase):
    """Model for creating a project."""

    preset: Literal["starter", "standard", "advanced", "budget", "custom"] = "standard"
    config: ProjectConfig | None = None


class ProjectUpdate(StudioBaseModel):
    """Model for updating a project."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: Literal["active", "paused", "archived"] | None = None
    config: ProjectConfig | None = None


class Project(ProjectBase, MongoBaseModel, TimestampMixin):
    """Project model for API responses."""

    user_id: str
    status: Literal["active", "paused", "error", "archived"] = "active"
    preset: str = "standard"
    config: ProjectConfig = Field(default_factory=ProjectConfig)
    stats: ProjectStats = Field(default_factory=ProjectStats)
    archived_at: datetime | None = None


class ProjectInDB(Project):
    """Project model with all database fields."""

    pass


class ProjectList(StudioBaseModel):
    """Paginated project list response."""

    items: list[Project]
    total: int
    page: int
    page_size: int
    pages: int
