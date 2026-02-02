"""Preset configuration service."""

from app.models.project import (
    ProjectConfig,
    ScraperConfig,
    LLMConfig,
    AnalysisConfig,
    ScheduleConfig,
    LimitsConfig,
)


PRESETS = {
    "starter": {
        "name": "Starter",
        "description": "Basic sentiment analysis for beginners",
        "config": ProjectConfig(
            scrapers=ScraperConfig(
                platforms=["amazon"],
                commercial_provider=None,
            ),
            llm=LLMConfig(
                provider="groq",
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=500,
            ),
            analysis=AnalysisConfig(
                sentiment=True,
                sentiment_classes=3,
                emotions=False,
                summarize=False,
                extract_insights=False,
            ),
            schedule=ScheduleConfig(enabled=False),
            limits=LimitsConfig(
                max_reviews_per_target=50,
                max_requests_per_day=100,
                rate_limit_delay=2.0,
            ),
        ),
    },
    "standard": {
        "name": "Standard",
        "description": "Comprehensive analysis for most use cases",
        "config": ProjectConfig(
            scrapers=ScraperConfig(
                platforms=["amazon", "steam", "youtube"],
                commercial_provider=None,
            ),
            llm=LLMConfig(
                provider="groq",
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=1000,
            ),
            analysis=AnalysisConfig(
                sentiment=True,
                sentiment_classes=5,
                emotions=True,
                emotion_model="ekman",
                summarize=False,
                extract_insights=False,
            ),
            schedule=ScheduleConfig(enabled=False),
            limits=LimitsConfig(
                max_reviews_per_target=100,
                max_requests_per_day=500,
                rate_limit_delay=1.0,
            ),
        ),
    },
    "advanced": {
        "name": "Advanced",
        "description": "Full-featured analysis with all options",
        "config": ProjectConfig(
            scrapers=ScraperConfig(
                platforms=["amazon", "steam", "youtube", "reddit", "trustpilot"],
                commercial_provider="scraperapi",
            ),
            llm=LLMConfig(
                provider="groq",
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=2000,
            ),
            analysis=AnalysisConfig(
                sentiment=True,
                sentiment_classes=5,
                emotions=True,
                emotion_model="goemotions",
                summarize=True,
                extract_insights=True,
            ),
            schedule=ScheduleConfig(
                enabled=True,
                frequency="daily",
                time="09:00",
            ),
            limits=LimitsConfig(
                max_reviews_per_target=200,
                max_requests_per_day=1000,
                rate_limit_delay=0.5,
            ),
        ),
    },
    "budget": {
        "name": "Budget",
        "description": "Cost-effective analysis with minimal API usage",
        "config": ProjectConfig(
            scrapers=ScraperConfig(
                platforms=["amazon"],
                commercial_provider=None,
            ),
            llm=LLMConfig(
                provider="groq",
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=300,
            ),
            analysis=AnalysisConfig(
                sentiment=True,
                sentiment_classes=3,
                emotions=False,
                summarize=False,
                extract_insights=False,
            ),
            schedule=ScheduleConfig(enabled=False),
            limits=LimitsConfig(
                max_reviews_per_target=25,
                max_requests_per_day=50,
                rate_limit_delay=3.0,
            ),
        ),
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "Maximum throughput for enterprise needs",
        "config": ProjectConfig(
            scrapers=ScraperConfig(
                platforms=["amazon", "steam", "youtube", "reddit", "trustpilot", "yelp", "google"],
                commercial_provider="scraperapi",
            ),
            llm=LLMConfig(
                provider="openai",
                model="gpt-4o-mini",
                temperature=0.5,
                max_tokens=4000,
            ),
            analysis=AnalysisConfig(
                sentiment=True,
                sentiment_classes=5,
                emotions=True,
                emotion_model="goemotions",
                summarize=True,
                extract_insights=True,
            ),
            schedule=ScheduleConfig(
                enabled=True,
                frequency="hourly",
            ),
            limits=LimitsConfig(
                max_reviews_per_target=500,
                max_requests_per_day=5000,
                rate_limit_delay=0.2,
            ),
        ),
    },
}


def get_preset_config(preset_name: str) -> ProjectConfig | None:
    """Get configuration for a preset."""
    preset = PRESETS.get(preset_name)
    if preset:
        return preset["config"]
    return None


def get_all_presets() -> list[dict]:
    """Get all available presets."""
    return [
        {
            "id": key,
            "name": value["name"],
            "description": value["description"],
        }
        for key, value in PRESETS.items()
    ]


def get_preset_details(preset_name: str) -> dict | None:
    """Get full preset details including config."""
    preset = PRESETS.get(preset_name)
    if preset:
        return {
            "id": preset_name,
            "name": preset["name"],
            "description": preset["description"],
            "config": preset["config"].model_dump(),
        }
    return None
