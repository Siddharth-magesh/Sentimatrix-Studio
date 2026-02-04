"""Sentimatrix integration service."""

import logging
import re
from datetime import datetime, timezone
from typing import Any

from sentimatrix import Sentimatrix, SentimatrixConfig, LLMConfig as SMLLMConfig, ScraperConfig as SMScraperConfig

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
        from sentimatrix.core.config import LLMProvider, ScraperProvider

        # Map string provider to LLMProvider enum
        llm_provider_map = {
            "openai": LLMProvider.OPENAI,
            "anthropic": LLMProvider.ANTHROPIC,
            "gemini": LLMProvider.GEMINI,
            "azure_openai": LLMProvider.AZURE_OPENAI,
            "bedrock": LLMProvider.BEDROCK,
            "groq": LLMProvider.GROQ,
            "cerebras": LLMProvider.CEREBRAS,
            "fireworks": LLMProvider.FIREWORKS,
            "together": LLMProvider.TOGETHER,
            "openrouter": LLMProvider.OPENROUTER,
            "mistral": LLMProvider.MISTRAL,
            "cohere": LLMProvider.COHERE,
            "deepseek": LLMProvider.DEEPSEEK,
            "ollama": LLMProvider.OLLAMA,
            "lmstudio": LLMProvider.LMSTUDIO,
            "huggingface": LLMProvider.HUGGINGFACE,
        }

        provider_str = self.llm_config.provider.lower()
        llm_provider = llm_provider_map.get(provider_str, LLMProvider.GROQ)

        # Build LLM config for sentimatrix
        llm_config = SMLLMConfig(
            provider=llm_provider,
            model=self.llm_config.model,
            temperature=self.llm_config.temperature,
            max_tokens=self.llm_config.max_tokens,
        )

        # Map commercial provider to ScraperProvider enum
        scraper_provider_map = {
            "playwright": ScraperProvider.PLAYWRIGHT,
            "selenium": ScraperProvider.SELENIUM,
            "httpx": ScraperProvider.HTTPX,
            "requests": ScraperProvider.REQUESTS,
            "scraperapi": ScraperProvider.SCRAPERAPI,
            "brightdata": ScraperProvider.BRIGHTDATA,
            "oxylabs": ScraperProvider.OXYLABS,
            "apify": ScraperProvider.APIFY,
            "zyte": ScraperProvider.ZYTE,
            "firecrawl": ScraperProvider.FIRECRAWL,
            "scrapingbee": ScraperProvider.SCRAPERAPI,  # Fallback
        }

        # Build scraper config with commercial provider if specified
        scraper_kwargs: dict[str, Any] = {
            "headless": True,
            "timeout": 30,
        }

        if self.commercial_provider:
            provider_value = scraper_provider_map.get(
                self.commercial_provider.lower(),
                ScraperProvider.PLAYWRIGHT
            )
            scraper_kwargs["provider"] = provider_value
        else:
            scraper_kwargs["provider"] = ScraperProvider.PLAYWRIGHT

        scraper_config = SMScraperConfig(**scraper_kwargs)

        # Create SentimatrixConfig with nested configs
        sm_config = SentimatrixConfig(
            llm=llm_config,
            scrapers=scraper_config,
        )

        self._client = Sentimatrix(config=sm_config)
        await self._client.initialize()

    async def close(self) -> None:
        """Close the Sentimatrix client."""
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> Sentimatrix:
        """Get the Sentimatrix client instance."""
        if not self._client:
            raise RuntimeError("SentimatrixService not initialized. Use async context manager.")
        return self._client

    def _extract_amazon_asin(self, url: str) -> str | None:
        """Extract ASIN from Amazon URL."""
        # Match patterns like /dp/ASIN or /product/ASIN
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def _extract_steam_app_id(self, url: str) -> str | None:
        """Extract app ID from Steam URL."""
        match = re.search(r'/app/(\d+)', url)
        return match.group(1) if match else None

    def _extract_youtube_video_id(self, url: str) -> str | None:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'/embed/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _extract_reddit_post_id(self, url: str) -> str | None:
        """Extract post ID from Reddit URL."""
        match = re.search(r'/comments/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else None

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
            platform: Platform hint (amazon, steam, youtube, reddit)
            max_results: Maximum number of results to scrape

        Returns:
            List of scraped content dictionaries
        """
        max_results = max_results or self.limits_config.max_reviews_per_target

        try:
            results = []

            if platform == "amazon":
                asin = self._extract_amazon_asin(url)
                if not asin:
                    raise ValueError(f"Could not extract ASIN from Amazon URL: {url}")
                reviews = await self.client.scrape_amazon(
                    asin=asin,
                    limit=max_results,
                    country=kwargs.get("country", "us"),
                )
                results = [self._review_to_dict(r) for r in reviews]

            elif platform == "steam":
                app_id = self._extract_steam_app_id(url)
                if not app_id:
                    raise ValueError(f"Could not extract app ID from Steam URL: {url}")
                reviews = await self.client.scrape_steam(
                    app_id=app_id,
                    limit=max_results,
                    language=kwargs.get("language", "english"),
                )
                results = [self._review_to_dict(r) for r in reviews]

            elif platform == "youtube":
                video_id = self._extract_youtube_video_id(url)
                if not video_id:
                    raise ValueError(f"Could not extract video ID from YouTube URL: {url}")
                reviews = await self.client.scrape_youtube(
                    video_id=video_id,
                    limit=max_results,
                    api_key=kwargs.get("api_key"),
                )
                results = [self._review_to_dict(r) for r in reviews]

            elif platform == "reddit":
                post_id = self._extract_reddit_post_id(url)
                if not post_id:
                    raise ValueError(f"Could not extract post ID from Reddit URL: {url}")
                reviews = await self.client.scrape_reddit(
                    post_id=post_id,
                    limit=max_results,
                )
                results = [self._review_to_dict(r) for r in reviews]

            else:
                # Try to auto-detect platform from URL
                if "amazon" in url.lower():
                    return await self.scrape_url(url, "amazon", max_results, **kwargs)
                elif "steampowered.com" in url.lower():
                    return await self.scrape_url(url, "steam", max_results, **kwargs)
                elif "youtube.com" in url.lower() or "youtu.be" in url.lower():
                    return await self.scrape_url(url, "youtube", max_results, **kwargs)
                elif "reddit.com" in url.lower():
                    return await self.scrape_url(url, "reddit", max_results, **kwargs)
                else:
                    raise ValueError(
                        f"Unsupported platform. URL: {url}. "
                        "Supported platforms: amazon, steam, youtube, reddit"
                    )

            return results

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise

    def _review_to_dict(self, review: Any) -> dict[str, Any]:
        """Convert a sentimatrix Review object to dictionary."""
        if hasattr(review, "model_dump"):
            return review.model_dump()
        elif hasattr(review, "dict"):
            return review.dict()
        elif hasattr(review, "__dict__"):
            return {k: v for k, v in review.__dict__.items() if not k.startswith("_")}
        return dict(review) if isinstance(review, dict) else {"text": str(review)}

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
            include_emotions = self.analysis_config.emotions

            # Full analysis using sentimatrix
            sm_result = await self.client.analyze(text, include_emotions=include_emotions)

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
            # Batch sentiment analysis using actual sentimatrix API
            if self.analysis_config.sentiment:
                batch_result = await self.client.analyze_sentiment_batch(
                    texts, batch_size=batch_size
                )

                # batch_result.results contains SentimentResult objects
                for sm_sentiment in batch_result.results:
                    result = AnalysisResult(
                        sentiment=self._convert_sentiment(sm_sentiment, now)
                    )
                    results.append(result)

                # Add emotions if enabled using batch emotion detection
                if self.analysis_config.emotions:
                    emotion_batch = await self.client.detect_emotions_batch(
                        texts, batch_size=batch_size
                    )
                    for i, emotion_result in enumerate(emotion_batch.results):
                        if i < len(results):
                            results[i].emotions = self._convert_emotions(emotion_result, now)
            else:
                # Just emotions using batch detection
                if self.analysis_config.emotions:
                    emotion_batch = await self.client.detect_emotions_batch(
                        texts, batch_size=batch_size
                    )
                    for emotion_result in emotion_batch.results:
                        result = AnalysisResult(
                            emotions=self._convert_emotions(emotion_result, now)
                        )
                        results.append(result)

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise

        return results

    async def analyze_reviews(
        self,
        scraped_data: list[dict[str, Any]],
    ) -> list[AnalysisResult]:
        """
        Analyze scraped reviews using sentimatrix's analyze_reviews.

        Args:
            scraped_data: List of scraped review dictionaries

        Returns:
            List of AnalysisResult objects
        """
        now = datetime.now(timezone.utc)
        results = []

        try:
            # Import Review from correct location
            from sentimatrix.main import Review
            import uuid

            reviews = []
            for data in scraped_data:
                # Review requires: id, text, source, platform
                # Optional: author, rating, timestamp, metadata
                review = Review(
                    id=data.get("id") or data.get("review_id") or str(uuid.uuid4()),
                    text=data.get("text", data.get("content", "")),
                    source=data.get("url") or data.get("source") or "unknown",
                    platform=data.get("platform") or "unknown",
                    author=data.get("author"),
                    rating=data.get("rating"),
                    timestamp=data.get("timestamp") or data.get("date"),
                    metadata=data.get("metadata", {}),
                )
                reviews.append(review)

            # Use sentimatrix's analyze_reviews for batch processing
            sm_result = await self.client.analyze_reviews(
                reviews,
                include_emotions=self.analysis_config.emotions,
            )

            # Convert results
            for review_result in sm_result.reviews:
                result = AnalysisResult()

                if review_result.sentiment and self.analysis_config.sentiment:
                    result.sentiment = self._convert_sentiment(review_result.sentiment, now)

                if review_result.emotions and self.analysis_config.emotions:
                    result.emotions = self._convert_emotions(review_result.emotions, now)

                results.append(result)

        except Exception as e:
            logger.error(f"Error analyzing reviews: {e}")
            # Fallback to batch analysis
            texts = [d.get("text", d.get("content", "")) for d in scraped_data]
            return await self.analyze_batch(texts)

        return results

    def _convert_sentiment(self, sm_sentiment: Any, analyzed_at: datetime) -> SentimentAnalysis:
        """Convert Sentimatrix sentiment result to our model."""
        # Get the sentiment label
        label = "neutral"
        if hasattr(sm_sentiment, "sentiment"):
            if hasattr(sm_sentiment.sentiment, "value"):
                label = str(sm_sentiment.sentiment.value).lower()
            else:
                label = str(sm_sentiment.sentiment).lower()

        if label not in ("positive", "neutral", "negative"):
            label = "neutral"

        # Get confidence score
        confidence = getattr(sm_sentiment, "confidence", 0.5)

        # Calculate score from -1 to 1 using all_scores if available
        score = 0.0
        all_scores = getattr(sm_sentiment, "all_scores", {}) or {}

        if all_scores:
            positive = all_scores.get("positive", 0)
            negative = all_scores.get("negative", 0)
            score = positive - negative
        else:
            # Estimate from label
            score = {"positive": 0.7, "neutral": 0.0, "negative": -0.7}.get(label, 0.0)

        # Build detailed scores if 5-class analysis is enabled
        scores = None
        if self.analysis_config.sentiment_classes == 5:
            scores = SentimentScores(
                very_positive=all_scores.get("very_positive", max(0, score) * 0.5),
                positive=all_scores.get("positive", max(0, score) * 0.5),
                neutral=all_scores.get("neutral", 1.0 - abs(score)),
                negative=all_scores.get("negative", max(0, -score) * 0.5),
                very_negative=all_scores.get("very_negative", max(0, -score) * 0.5),
            )

        return SentimentAnalysis(
            label=label,
            score=score,
            confidence=confidence,
            scores=scores,
            analyzed_at=analyzed_at,
        )

    def _convert_emotions(self, sm_emotions: Any, analyzed_at: datetime) -> EmotionAnalysis:
        """Convert Sentimatrix emotion result to our model.

        Sentimatrix EmotionResult has:
        - primary_emotion: EmotionScore (label, score, category, valence, ekman_mapping)
        - emotions: List[EmotionScore]
        - all_scores: Dict[str, float]
        - model_name: str
        """
        # Get primary emotion from primary_emotion field
        primary = None
        primary_score = None

        primary_emotion = getattr(sm_emotions, "primary_emotion", None)
        if primary_emotion:
            primary = getattr(primary_emotion, "label", None)
            primary_score = getattr(primary_emotion, "score", None)

        # Get all detected emotions from emotions list
        detected = []
        threshold = 0.1  # Minimum score to include

        # emotions is a List[EmotionScore] with label and score fields
        emotions_list = getattr(sm_emotions, "emotions", []) or []

        for emotion_item in emotions_list:
            emotion_label = getattr(emotion_item, "label", None)
            emotion_score = getattr(emotion_item, "score", 0)

            if emotion_label and emotion_score >= threshold and emotion_label.lower() != "neutral":
                detected.append(EmotionDetected(emotion=emotion_label, score=emotion_score))

        # Also check all_scores dict if available (fallback)
        if not detected:
            all_scores = getattr(sm_emotions, "all_scores", {}) or {}
            for label, score in all_scores.items():
                if score >= threshold and label.lower() != "neutral":
                    detected.append(EmotionDetected(emotion=label, score=score))

        # Sort by score descending
        detected.sort(key=lambda x: x.score, reverse=True)

        # Get model name
        model_name = getattr(sm_emotions, "model_name", "unknown")

        return EmotionAnalysis(
            model=model_name,
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
