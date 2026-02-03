"""Sentimatrix integration service."""

import logging
from datetime import datetime, timezone
from typing import Any

from sentimatrix import Sentimatrix, SentimatrixConfig, ScraperConfig as SMScraperConfig

from app.models.project import LLMConfig, AnalysisConfig, LimitsConfig
from app.models.result import (
    AnalysisResult,
    EmotionAnalysis,
    EmotionDetected,
    ResultContent,
    SentimentAnalysis,
    SentimentScores,
)

logger = logging.getLogger(__name__)


class SentimatrixService:
    """Service for interacting with Sentimatrix library."""

    def __init__(
        self,
        llm_config: LLMConfig | None = None,
        analysis_config: AnalysisConfig | None = None,
        limits_config: LimitsConfig | None = None,
        commercial_provider: str | None = None,
    ):
        self.llm_config = llm_config or LLMConfig()
        self.analysis_config = analysis_config or AnalysisConfig()
        self.limits_config = limits_config or LimitsConfig()
        self.commercial_provider = commercial_provider
        self._client: Sentimatrix | None = None

    async def __aenter__(self) -> "SentimatrixService":
        """Async context manager entry."""
        await self._init_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def _init_client(self) -> None:
        """Initialize Sentimatrix client with configuration."""
        # Build Sentimatrix config
        config_kwargs: dict[str, Any] = {
            "llm_provider": self.llm_config.provider,
            "llm_model": self.llm_config.model,
            "llm_temperature": self.llm_config.temperature,
            "llm_max_tokens": self.llm_config.max_tokens,
        }

        # Add commercial scraper if configured
        if self.commercial_provider:
            scraper_config = SMScraperConfig(
                commercial_provider=self.commercial_provider,
                rate_limit=self.limits_config.rate_limit_delay,
            )
            config_kwargs["scraper_config"] = scraper_config

        sm_config = SentimatrixConfig(**config_kwargs)
        self._client = Sentimatrix(config=sm_config)
        await self._client.__aenter__()

    async def close(self) -> None:
        """Close the Sentimatrix client."""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    @property
    def client(self) -> Sentimatrix:
        """Get the Sentimatrix client instance."""
        if not self._client:
            raise RuntimeError("SentimatrixService not initialized. Use async context manager.")
        return self._client

    async def scrape_url(
        self,
        url: str,
        platform: str | None = None,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Scrape content from a URL using Sentimatrix.

        Args:
            url: The URL to scrape
            platform: Platform hint (amazon, steam, youtube, etc.)
            max_results: Maximum number of results to scrape

        Returns:
            List of scraped content dictionaries
        """
        max_results = max_results or self.limits_config.max_reviews_per_target

        try:
            # Use platform-specific scraper if available
            if platform == "amazon":
                results = await self.client.scrape_amazon_reviews(
                    url, max_reviews=max_results, **kwargs
                )
            elif platform == "steam":
                results = await self.client.scrape_steam_reviews(
                    url, max_reviews=max_results, **kwargs
                )
            elif platform == "youtube":
                results = await self.client.scrape_youtube_comments(
                    url, max_comments=max_results, **kwargs
                )
            elif platform == "reddit":
                results = await self.client.scrape_reddit_comments(
                    url, max_comments=max_results, **kwargs
                )
            elif platform == "trustpilot":
                results = await self.client.scrape_trustpilot_reviews(
                    url, max_reviews=max_results, **kwargs
                )
            elif platform == "yelp":
                results = await self.client.scrape_yelp_reviews(
                    url, max_reviews=max_results, **kwargs
                )
            elif platform == "google":
                results = await self.client.scrape_google_reviews(
                    url, max_reviews=max_results, **kwargs
                )
            else:
                # Generic scraper
                results = await self.client.scrape_reviews(
                    url, max_reviews=max_results, **kwargs
                )

            # Convert to list of dicts
            if hasattr(results, "to_dict"):
                return [results.to_dict()]
            elif isinstance(results, list):
                return [
                    r.to_dict() if hasattr(r, "to_dict") else r
                    for r in results
                ]
            return results if isinstance(results, list) else [results]

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise

    async def analyze_text(self, text: str) -> AnalysisResult:
        """
        Analyze text using Sentimatrix.

        Args:
            text: The text to analyze

        Returns:
            AnalysisResult with sentiment and emotion data
        """
        result = AnalysisResult()
        now = datetime.now(timezone.utc)

        try:
            # Full analysis
            sm_result = await self.client.analyze(text)

            # Process sentiment
            if sm_result.sentiment and self.analysis_config.sentiment:
                result.sentiment = self._convert_sentiment(sm_result.sentiment, now)

            # Process emotions
            if sm_result.emotions and self.analysis_config.emotions:
                result.emotions = self._convert_emotions(sm_result.emotions, now)

        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            raise

        return result

    async def analyze_batch(
        self,
        texts: list[str],
        batch_size: int = 10,
    ) -> list[AnalysisResult]:
        """
        Analyze multiple texts in batch.

        Args:
            texts: List of texts to analyze
            batch_size: Number of texts per batch

        Returns:
            List of AnalysisResult objects
        """
        results = []
        now = datetime.now(timezone.utc)

        try:
            # Batch sentiment analysis
            if self.analysis_config.sentiment:
                batch_result = await self.client.analyze_sentiment_batch(
                    texts, batch_size=batch_size
                )

                for sm_sentiment in batch_result.results:
                    result = AnalysisResult(
                        sentiment=self._convert_sentiment(sm_sentiment, now)
                    )
                    results.append(result)

                # Add emotions if enabled
                if self.analysis_config.emotions:
                    for i, text in enumerate(texts):
                        emotion_result = await self.client.analyze_emotions(text)
                        results[i].emotions = self._convert_emotions(emotion_result, now)
            else:
                # Just emotions
                for text in texts:
                    emotion_result = await self.client.analyze_emotions(text)
                    result = AnalysisResult(
                        emotions=self._convert_emotions(emotion_result, now)
                    )
                    results.append(result)

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise

        return results

    def _convert_sentiment(self, sm_sentiment: Any, analyzed_at: datetime) -> SentimentAnalysis:
        """Convert Sentimatrix sentiment result to our model."""
        # Map sentiment label
        label = str(sm_sentiment.sentiment.value).lower()
        if label not in ("positive", "neutral", "negative"):
            label = "neutral"

        # Calculate score from -1 to 1
        all_scores = sm_sentiment.all_scores or {}
        positive = all_scores.get("positive", 0)
        negative = all_scores.get("negative", 0)
        score = positive - negative

        # Build detailed scores if 5-class analysis
        scores = None
        if self.analysis_config.sentiment_classes == 5:
            scores = SentimentScores(
                very_positive=all_scores.get("very_positive", positive * 0.5),
                positive=all_scores.get("positive", positive * 0.5),
                neutral=all_scores.get("neutral", 0),
                negative=all_scores.get("negative", negative * 0.5),
                very_negative=all_scores.get("very_negative", negative * 0.5),
            )

        return SentimentAnalysis(
            label=label,
            score=score,
            confidence=sm_sentiment.confidence,
            scores=scores,
            analyzed_at=analyzed_at,
        )

    def _convert_emotions(self, sm_emotions: Any, analyzed_at: datetime) -> EmotionAnalysis:
        """Convert Sentimatrix emotion result to our model."""
        # Get primary emotion
        primary = None
        primary_score = None
        if sm_emotions.primary_emotion:
            primary = sm_emotions.primary_emotion.label
            primary_score = sm_emotions.primary_emotion.score

        # Get all detected emotions above threshold
        detected = []
        threshold = 0.1  # Minimum score to include
        if sm_emotions.all_scores:
            for label, score in sm_emotions.all_scores.items():
                if score >= threshold and label != "neutral":
                    detected.append(EmotionDetected(emotion=label, score=score))
            # Sort by score descending
            detected.sort(key=lambda x: x.score, reverse=True)

        return EmotionAnalysis(
            model=sm_emotions.model_name,
            primary=primary,
            primary_score=primary_score,
            detected=detected[:10],  # Top 10 emotions
            analyzed_at=analyzed_at,
        )

    def parse_scraped_content(self, raw_data: dict[str, Any]) -> ResultContent:
        """
        Parse raw scraped data into ResultContent model.

        Args:
            raw_data: Raw scraped data from Sentimatrix

        Returns:
            ResultContent model
        """
        # Handle different platform data formats
        text = raw_data.get("text") or raw_data.get("content") or raw_data.get("body", "")
        title = raw_data.get("title") or raw_data.get("headline")
        author = (
            raw_data.get("author")
            or raw_data.get("username")
            or raw_data.get("reviewer")
        )

        # Parse rating (different platforms use different scales)
        rating = None
        if "rating" in raw_data:
            rating = float(raw_data["rating"])
        elif "score" in raw_data:
            # Steam uses 0/1, convert to 5-star
            score = raw_data["score"]
            rating = 5.0 if score else 1.0
        elif "stars" in raw_data:
            rating = float(raw_data["stars"])

        # Parse date
        date = None
        date_str = raw_data.get("date") or raw_data.get("created_at") or raw_data.get("timestamp")
        if date_str:
            if isinstance(date_str, datetime):
                date = date_str
            else:
                try:
                    date = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

        return ResultContent(
            text=text,
            title=title,
            author=author,
            rating=rating,
            date=date,
            url=raw_data.get("url") or raw_data.get("link"),
            platform_id=raw_data.get("id") or raw_data.get("review_id"),
        )


async def get_sentimatrix_service(
    llm_config: LLMConfig | None = None,
    analysis_config: AnalysisConfig | None = None,
    limits_config: LimitsConfig | None = None,
    commercial_provider: str | None = None,
) -> SentimatrixService:
    """Factory function to create SentimatrixService."""
    service = SentimatrixService(
        llm_config=llm_config,
        analysis_config=analysis_config,
        limits_config=limits_config,
        commercial_provider=commercial_provider,
    )
    await service._init_client()
    return service
