"""Result model definitions."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class ResultContent(StudioBaseModel):
    """Original scraped content."""

    text: str
    title: str | None = None
    author: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    date: datetime | None = None
    url: str | None = None
    platform_id: str | None = None


class SentimentScores(StudioBaseModel):
    """Detailed sentiment scores for 5-class."""

    very_positive: float = 0.0
    positive: float = 0.0
    neutral: float = 0.0
    negative: float = 0.0
    very_negative: float = 0.0


class SentimentAnalysis(StudioBaseModel):
    """Sentiment analysis result."""

    label: Literal["positive", "neutral", "negative"] | None = None
    score: float | None = Field(default=None, ge=-1.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    scores: SentimentScores | None = None
    analyzed_at: datetime | None = None


class EmotionDetected(StudioBaseModel):
    """Single detected emotion."""

    emotion: str
    score: float = Field(ge=0.0, le=1.0)


class EmotionAnalysis(StudioBaseModel):
    """Emotion analysis result."""

    model: str | None = None
    primary: str | None = None
    primary_score: float | None = None
    detected: list[EmotionDetected] = Field(default_factory=list)
    analyzed_at: datetime | None = None


class SummaryAnalysis(StudioBaseModel):
    """Summary analysis result."""

    text: str | None = None
    key_points: list[str] = Field(default_factory=list)
    generated_at: datetime | None = None


class TopicSentiment(StudioBaseModel):
    """Topic with its sentiment."""

    topic: str
    sentiment: float = Field(ge=-1.0, le=1.0)


class InsightsAnalysis(StudioBaseModel):
    """Insights extraction result."""

    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    topics: list[TopicSentiment] = Field(default_factory=list)
    extracted_at: datetime | None = None


class AnalysisResult(StudioBaseModel):
    """Complete analysis result."""

    sentiment: SentimentAnalysis | None = None
    emotions: EmotionAnalysis | None = None
    summary: SummaryAnalysis | None = None
    insights: InsightsAnalysis | None = None


class Result(MongoBaseModel, TimestampMixin):
    """Result model for API responses."""

    project_id: str
    target_id: str
    user_id: str
    scrape_job_id: str | None = None
    content: ResultContent
    analysis: AnalysisResult = Field(default_factory=AnalysisResult)
    platform: str | None = None
    language: str | None = None
    word_count: int | None = None


class ResultInDB(Result):
    """Result model with all database fields."""

    pass


class ResultList(StudioBaseModel):
    """Paginated result list response."""

    items: list[Result]
    total: int
    page: int
    page_size: int


class ResultFilter(StudioBaseModel):
    """Result filter options."""

    sentiment: Literal["positive", "neutral", "negative"] | None = None
    platform: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = None
    target_id: str | None = None


class ResultAggregation(StudioBaseModel):
    """Aggregated result statistics."""

    total_results: int = 0
    sentiment_distribution: dict[str, int] = Field(default_factory=dict)
    avg_sentiment_score: float | None = None
    avg_rating: float | None = None
    platforms: dict[str, int] = Field(default_factory=dict)
    date_range: dict[str, datetime | None] = Field(default_factory=dict)
