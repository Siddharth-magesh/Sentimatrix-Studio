"""LLM Provider model definitions."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from app.models.base import MongoBaseModel, StudioBaseModel, TimestampMixin


class LLMProviderModel(StudioBaseModel):
    """Model information for an LLM provider."""

    id: str
    name: str
    max_tokens: int = 4096
    supports_functions: bool = False
    supports_vision: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class LLMProviderInfo(StudioBaseModel):
    """Static information about an LLM provider."""

    id: str
    name: str
    description: str
    website: str
    requires_api_key: bool = True
    models: list[LLMProviderModel] = Field(default_factory=list)
    supported_features: list[str] = Field(default_factory=list)


# Available LLM providers
LLM_PROVIDERS: dict[str, LLMProviderInfo] = {
    "groq": LLMProviderInfo(
        id="groq",
        name="Groq",
        description="Ultra-fast LLM inference with open-source models",
        website="https://groq.com",
        requires_api_key=True,
        models=[
            LLMProviderModel(
                id="llama-3.3-70b-versatile",
                name="Llama 3.3 70B Versatile",
                max_tokens=8192,
                supports_functions=True,
            ),
            LLMProviderModel(
                id="llama-3.1-8b-instant",
                name="Llama 3.1 8B Instant",
                max_tokens=8192,
                supports_functions=True,
            ),
            LLMProviderModel(
                id="mixtral-8x7b-32768",
                name="Mixtral 8x7B",
                max_tokens=32768,
                supports_functions=True,
            ),
        ],
        supported_features=["sentiment", "emotions", "summarization", "insights"],
    ),
    "openai": LLMProviderInfo(
        id="openai",
        name="OpenAI",
        description="GPT models for natural language processing",
        website="https://openai.com",
        requires_api_key=True,
        models=[
            LLMProviderModel(
                id="gpt-4o-mini",
                name="GPT-4o Mini",
                max_tokens=16384,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
            ),
            LLMProviderModel(
                id="gpt-4o",
                name="GPT-4o",
                max_tokens=16384,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
            ),
            LLMProviderModel(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                max_tokens=4096,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
            ),
        ],
        supported_features=["sentiment", "emotions", "summarization", "insights", "vision"],
    ),
    "anthropic": LLMProviderInfo(
        id="anthropic",
        name="Anthropic",
        description="Claude models for safe and helpful AI",
        website="https://anthropic.com",
        requires_api_key=True,
        models=[
            LLMProviderModel(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                max_tokens=8192,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
            ),
            LLMProviderModel(
                id="claude-3-5-haiku-20241022",
                name="Claude 3.5 Haiku",
                max_tokens=8192,
                supports_functions=True,
                supports_vision=True,
                cost_per_1k_input=0.0008,
                cost_per_1k_output=0.004,
            ),
        ],
        supported_features=["sentiment", "emotions", "summarization", "insights", "vision"],
    ),
    "local": LLMProviderInfo(
        id="local",
        name="Local (Ollama)",
        description="Run models locally with Ollama",
        website="https://ollama.ai",
        requires_api_key=False,
        models=[
            LLMProviderModel(
                id="llama3.2",
                name="Llama 3.2",
                max_tokens=4096,
            ),
            LLMProviderModel(
                id="mistral",
                name="Mistral 7B",
                max_tokens=4096,
            ),
        ],
        supported_features=["sentiment", "emotions"],
    ),
    "scraperapi": LLMProviderInfo(
        id="scraperapi",
        name="ScraperAPI",
        description="Web scraping API service",
        website="https://scraperapi.com",
        requires_api_key=True,
        models=[],
        supported_features=["scraping"],
    ),
    "apify": LLMProviderInfo(
        id="apify",
        name="Apify",
        description="Web scraping and automation platform",
        website="https://apify.com",
        requires_api_key=True,
        models=[],
        supported_features=["scraping"],
    ),
    "scrapingbee": LLMProviderInfo(
        id="scrapingbee",
        name="ScrapingBee",
        description="Web scraping API with headless browsers",
        website="https://scrapingbee.com",
        requires_api_key=True,
        models=[],
        supported_features=["scraping"],
    ),
}


class APIKeyCreate(StudioBaseModel):
    """Model for creating/updating an API key."""

    provider: str
    api_key: str
    label: str | None = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider is supported."""
        if v not in LLM_PROVIDERS:
            raise ValueError(f"Unsupported provider: {v}")
        return v


class APIKeyResponse(StudioBaseModel):
    """API key response (masked)."""

    id: str
    provider: str
    label: str | None = None
    masked_key: str
    is_valid: bool | None = None
    last_used: datetime | None = None
    created_at: datetime


class APIKey(MongoBaseModel, TimestampMixin):
    """API key stored in database."""

    user_id: str
    provider: str
    encrypted_key: str  # Encrypted API key
    label: str | None = None
    is_valid: bool | None = None
    last_used: datetime | None = None
    last_validated: datetime | None = None


class APIKeyInDB(APIKey):
    """API key with all database fields."""

    pass


class LLMConnectionTest(StudioBaseModel):
    """Result of testing an LLM connection."""

    provider: str
    model: str
    success: bool
    latency_ms: float | None = None
    error: str | None = None
    tested_at: datetime


class UserLLMSettings(StudioBaseModel):
    """User's LLM configuration settings."""

    default_provider: str = "groq"
    default_model: str = "llama-3.3-70b-versatile"
    fallback_provider: str | None = None
    fallback_model: str | None = None
    auto_fallback: bool = True
