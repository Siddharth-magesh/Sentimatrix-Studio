"""Tests for configuration module."""

import pytest

from app.core.config import Settings


class TestSettings:
    """Test settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.app_name == "Sentimatrix Studio"
        assert settings.app_env == "development"
        assert settings.debug is False
        assert settings.port == 8000

    def test_mongodb_url_validation_valid(self):
        """Test valid MongoDB URLs."""
        settings = Settings(mongodb_url="mongodb://localhost:27017")
        assert settings.mongodb_url == "mongodb://localhost:27017"

        settings = Settings(mongodb_url="mongodb+srv://cluster.mongodb.net")
        assert settings.mongodb_url == "mongodb+srv://cluster.mongodb.net"

    def test_mongodb_url_validation_invalid(self):
        """Test invalid MongoDB URL."""
        with pytest.raises(ValueError):
            Settings(mongodb_url="invalid://localhost:27017")

    def test_cors_origins_from_string(self):
        """Test parsing CORS origins from JSON string."""
        settings = Settings(cors_origins='["http://localhost:3000", "http://localhost:8000"]')
        assert settings.cors_origins == ["http://localhost:3000", "http://localhost:8000"]

    def test_cors_origins_from_csv(self):
        """Test parsing CORS origins from comma-separated string."""
        settings = Settings(cors_origins="http://localhost:3000, http://localhost:8000")
        assert settings.cors_origins == ["http://localhost:3000", "http://localhost:8000"]

    def test_is_development(self):
        """Test is_development property."""
        settings = Settings(app_env="development")
        assert settings.is_development is True
        assert settings.is_production is False

    def test_is_production(self):
        """Test is_production property."""
        settings = Settings(app_env="production")
        assert settings.is_production is True
        assert settings.is_development is False

    def test_oauth_enabled(self):
        """Test OAuth enabled properties."""
        # Not configured
        settings = Settings()
        assert settings.google_oauth_enabled is False
        assert settings.github_oauth_enabled is False

        # Configured
        settings = Settings(
            google_client_id="client_id",
            google_client_secret="client_secret",
        )
        assert settings.google_oauth_enabled is True
