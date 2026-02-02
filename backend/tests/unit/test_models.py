"""Tests for Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.project import (
    Project,
    ProjectConfig,
    ProjectCreate,
    ScraperConfig,
    LLMConfig,
    AnalysisConfig,
    LimitsConfig,
)
from app.models.target import Target, TargetCreate
from app.models.scrape_job import ScrapeJob, ScrapeJobOptions, TargetJobStatus
from app.models.result import (
    Result,
    ResultContent,
    SentimentAnalysis,
    EmotionAnalysis,
    EmotionDetected,
)


class TestProjectModels:
    """Test project-related models."""

    def test_project_create_default_preset(self):
        """Test project creation with default preset."""
        project = ProjectCreate(name="Test Project")

        assert project.name == "Test Project"
        assert project.preset == "standard"
        assert project.config is None

    def test_project_create_custom_preset(self):
        """Test project creation with custom preset."""
        config = ProjectConfig(
            scrapers=ScraperConfig(platforms=["amazon"]),
            llm=LLMConfig(provider="groq"),
        )
        project = ProjectCreate(
            name="Custom Project",
            preset="custom",
            config=config,
        )

        assert project.preset == "custom"
        assert project.config is not None
        assert project.config.scrapers.platforms == ["amazon"]

    def test_scraper_config_defaults(self):
        """Test scraper config default values."""
        config = ScraperConfig()

        assert config.platforms == []
        assert config.commercial_provider is None
        assert config.use_proxies is False

    def test_llm_config_defaults(self):
        """Test LLM config default values."""
        config = LLMConfig()

        assert config.provider == "groq"
        assert config.model == "llama-3.3-70b-versatile"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000

    def test_analysis_config_defaults(self):
        """Test analysis config default values."""
        config = AnalysisConfig()

        assert config.sentiment is True
        assert config.sentiment_classes == 3
        assert config.emotions is False
        assert config.summarize is False

    def test_limits_config_validation(self):
        """Test limits config value validation."""
        # Valid config
        config = LimitsConfig(
            max_reviews_per_target=100,
            max_requests_per_day=500,
            rate_limit_delay=1.0,
        )
        assert config.max_reviews_per_target == 100

        # Invalid - negative delay
        with pytest.raises(ValidationError):
            LimitsConfig(rate_limit_delay=-1.0)


class TestTargetModels:
    """Test target-related models."""

    def test_target_create_basic(self):
        """Test basic target creation."""
        target = TargetCreate(url="https://www.amazon.com/dp/B09V3KXJPB")

        assert target.url == "https://www.amazon.com/dp/B09V3KXJPB"
        assert target.label is None
        assert target.options == {}

    def test_target_create_with_label(self):
        """Test target creation with custom label."""
        target = TargetCreate(
            url="https://www.amazon.com/dp/B09V3KXJPB",
            label="iPhone 13 Pro",
        )

        assert target.label == "iPhone 13 Pro"

    def test_target_create_with_options(self):
        """Test target creation with options."""
        target = TargetCreate(
            url="https://www.amazon.com/dp/B09V3KXJPB",
            options={"max_pages": 5, "sort_by": "recent"},
        )

        assert target.options["max_pages"] == 5

    def test_target_model(self):
        """Test full target model."""
        target = Target(
            id="123456789012345678901234",
            project_id="project123",
            user_id="user123",
            url="https://www.amazon.com/dp/B09V3KXJPB",
            label="iPhone",
            platform="amazon",
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert target.platform == "amazon"
        assert target.status == "active"


class TestScrapeJobModels:
    """Test scrape job models."""

    def test_scrape_job_options_defaults(self):
        """Test scrape job options defaults."""
        options = ScrapeJobOptions()

        assert options.max_results == 100
        assert options.include_replies is False
        assert options.date_from is None

    def test_scrape_job_options_validation(self):
        """Test scrape job options validation."""
        # Valid range
        options = ScrapeJobOptions(max_results=500)
        assert options.max_results == 500

        # Invalid - too high
        with pytest.raises(ValidationError):
            ScrapeJobOptions(max_results=2000)

        # Invalid - too low
        with pytest.raises(ValidationError):
            ScrapeJobOptions(max_results=0)

    def test_target_job_status(self):
        """Test target job status model."""
        status = TargetJobStatus(
            target_id="target123",
            status="running",
            progress=50,
            results_count=25,
        )

        assert status.status == "running"
        assert status.progress == 50
        assert status.error is None


class TestResultModels:
    """Test result models."""

    def test_result_content(self):
        """Test result content model."""
        content = ResultContent(
            text="Great product!",
            title="5 Star Review",
            author="John Doe",
            rating=5.0,
            date=datetime.now(),
        )

        assert content.text == "Great product!"
        assert content.rating == 5.0

    def test_result_content_rating_validation(self):
        """Test result content rating validation."""
        # Valid rating
        content = ResultContent(text="Good", rating=4.5)
        assert content.rating == 4.5

        # Invalid - too high
        with pytest.raises(ValidationError):
            ResultContent(text="Good", rating=6.0)

        # Invalid - negative
        with pytest.raises(ValidationError):
            ResultContent(text="Good", rating=-1.0)

    def test_sentiment_analysis(self):
        """Test sentiment analysis model."""
        sentiment = SentimentAnalysis(
            label="positive",
            score=0.85,
            confidence=0.92,
            analyzed_at=datetime.now(),
        )

        assert sentiment.label == "positive"
        assert sentiment.score == 0.85

    def test_sentiment_analysis_score_validation(self):
        """Test sentiment score validation."""
        # Valid range
        sentiment = SentimentAnalysis(label="neutral", score=0.0, confidence=0.5)
        assert sentiment.score == 0.0

        # Invalid - out of range
        with pytest.raises(ValidationError):
            SentimentAnalysis(label="positive", score=1.5, confidence=0.5)

    def test_emotion_detected(self):
        """Test emotion detected model."""
        emotion = EmotionDetected(emotion="joy", score=0.85)

        assert emotion.emotion == "joy"
        assert emotion.score == 0.85

    def test_emotion_analysis(self):
        """Test emotion analysis model."""
        emotions = EmotionAnalysis(
            model="goemotions",
            primary="joy",
            primary_score=0.85,
            detected=[
                EmotionDetected(emotion="joy", score=0.85),
                EmotionDetected(emotion="love", score=0.45),
            ],
        )

        assert emotions.primary == "joy"
        assert len(emotions.detected) == 2

    def test_full_result_model(self):
        """Test full result model."""
        result = Result(
            id="123456789012345678901234",
            project_id="project123",
            target_id="target123",
            user_id="user123",
            content=ResultContent(text="Great product!", rating=5.0),
            platform="amazon",
            word_count=2,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert result.platform == "amazon"
        assert result.content.text == "Great product!"
        assert result.word_count == 2
