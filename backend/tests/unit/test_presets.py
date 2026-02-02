"""Tests for preset service."""

import pytest

from app.services.presets import (
    PRESETS,
    get_preset_config,
    get_all_presets,
    get_preset_details,
)


class TestPresets:
    """Test preset configuration service."""

    def test_all_presets_defined(self):
        """Test that all expected presets are defined."""
        expected_presets = ["starter", "standard", "advanced", "budget", "enterprise"]

        for preset in expected_presets:
            assert preset in PRESETS, f"Missing preset: {preset}"

    def test_get_preset_config_valid(self):
        """Test getting config for valid preset."""
        config = get_preset_config("standard")

        assert config is not None
        assert config.llm.provider == "groq"
        assert config.analysis.sentiment is True

    def test_get_preset_config_invalid(self):
        """Test getting config for invalid preset."""
        config = get_preset_config("nonexistent")

        assert config is None

    def test_get_all_presets(self):
        """Test getting all presets list."""
        presets = get_all_presets()

        assert len(presets) == len(PRESETS)
        for preset in presets:
            assert "id" in preset
            assert "name" in preset
            assert "description" in preset

    def test_get_preset_details(self):
        """Test getting full preset details."""
        details = get_preset_details("advanced")

        assert details is not None
        assert details["id"] == "advanced"
        assert details["name"] == "Advanced"
        assert "config" in details
        assert details["config"]["scrapers"]["commercial_provider"] == "scraperapi"

    def test_get_preset_details_invalid(self):
        """Test getting details for invalid preset."""
        details = get_preset_details("nonexistent")

        assert details is None

    def test_starter_preset_minimal(self):
        """Test starter preset has minimal features."""
        config = get_preset_config("starter")

        assert config.scrapers.platforms == ["amazon"]
        assert config.scrapers.commercial_provider is None
        assert config.analysis.sentiment_classes == 3
        assert config.analysis.emotions is False
        assert config.limits.max_reviews_per_target == 50

    def test_advanced_preset_full_features(self):
        """Test advanced preset has full features."""
        config = get_preset_config("advanced")

        assert len(config.scrapers.platforms) > 3
        assert config.scrapers.commercial_provider is not None
        assert config.analysis.sentiment_classes == 5
        assert config.analysis.emotions is True
        assert config.analysis.summarize is True
        assert config.schedule.enabled is True

    def test_budget_preset_cost_effective(self):
        """Test budget preset is cost-effective."""
        config = get_preset_config("budget")

        assert config.llm.model == "llama-3.1-8b-instant"
        assert config.llm.max_tokens == 300
        assert config.limits.max_reviews_per_target == 25
        assert config.limits.max_requests_per_day == 50

    def test_enterprise_preset_maximum(self):
        """Test enterprise preset has maximum settings."""
        config = get_preset_config("enterprise")

        assert len(config.scrapers.platforms) >= 7
        assert config.llm.provider == "openai"
        assert config.schedule.frequency == "hourly"
        assert config.limits.max_reviews_per_target == 500
        assert config.limits.max_requests_per_day == 5000

    def test_preset_configs_valid_models(self):
        """Test all preset configs are valid Pydantic models."""
        for preset_name in PRESETS.keys():
            config = get_preset_config(preset_name)
            assert config is not None

            # Verify it can be serialized
            config_dict = config.model_dump()
            assert "scrapers" in config_dict
            assert "llm" in config_dict
            assert "analysis" in config_dict
            assert "schedule" in config_dict
            assert "limits" in config_dict
