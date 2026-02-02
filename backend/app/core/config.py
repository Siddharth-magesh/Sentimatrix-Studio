"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, MongoDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Sentimatrix Studio")
    app_env: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me-in-production")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # MongoDB
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="sentimatrix_studio")

    @field_validator("mongodb_url")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB URL format."""
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MongoDB URL must start with mongodb:// or mongodb+srv://")
        return v

    # JWT Authentication
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_window_seconds: int = Field(default=60)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_format: Literal["json", "console"] = Field(default="json")

    # Sentimatrix
    sentimatrix_default_llm_provider: str = Field(default="groq")
    sentimatrix_default_llm_model: str = Field(default="llama-3.3-70b-versatile")

    # OAuth2 (Optional)
    google_client_id: str | None = Field(default=None)
    google_client_secret: str | None = Field(default=None)
    github_client_id: str | None = Field(default=None)
    github_client_secret: str | None = Field(default=None)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def google_oauth_enabled(self) -> bool:
        """Check if Google OAuth is configured."""
        return bool(self.google_client_id and self.google_client_secret)

    @property
    def github_oauth_enabled(self) -> bool:
        """Check if GitHub OAuth is configured."""
        return bool(self.github_client_id and self.github_client_secret)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
