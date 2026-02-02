"""Tests for LLM provider models and configuration."""

import pytest
from pydantic import ValidationError

from app.models.llm_provider import (
    APIKeyCreate,
    APIKeyResponse,
    LLMProviderInfo,
    LLMProviderModel,
    LLM_PROVIDERS,
)


class TestLLMProviders:
    """Test LLM provider configuration."""

    def test_all_providers_defined(self):
        """Test that all expected providers are defined."""
        expected = ["groq", "openai", "anthropic", "local"]

        for provider in expected:
            assert provider in LLM_PROVIDERS

    def test_provider_info_structure(self):
        """Test provider info has required fields."""
        for provider_id, info in LLM_PROVIDERS.items():
            assert isinstance(info, LLMProviderInfo)
            assert info.id == provider_id
            assert info.name
            assert info.description
            assert info.website.startswith("http")
            assert len(info.models) > 0

    def test_groq_provider(self):
        """Test Groq provider configuration."""
        groq = LLM_PROVIDERS["groq"]

        assert groq.requires_api_key is True
        assert "llama-3.3-70b-versatile" in [m.id for m in groq.models]
        assert "sentiment" in groq.supported_features

    def test_openai_provider(self):
        """Test OpenAI provider configuration."""
        openai = LLM_PROVIDERS["openai"]

        assert openai.requires_api_key is True
        assert "gpt-4o-mini" in [m.id for m in openai.models]
        assert "vision" in openai.supported_features

    def test_anthropic_provider(self):
        """Test Anthropic provider configuration."""
        anthropic = LLM_PROVIDERS["anthropic"]

        assert anthropic.requires_api_key is True
        model_ids = [m.id for m in anthropic.models]
        assert any("claude" in m for m in model_ids)

    def test_local_provider(self):
        """Test local (Ollama) provider configuration."""
        local = LLM_PROVIDERS["local"]

        assert local.requires_api_key is False
        assert "ollama" in local.name.lower()

    def test_model_structure(self):
        """Test model info has required fields."""
        for info in LLM_PROVIDERS.values():
            for model in info.models:
                assert isinstance(model, LLMProviderModel)
                assert model.id
                assert model.name
                assert model.max_tokens > 0


class TestAPIKeyCreate:
    """Test API key creation model."""

    def test_valid_api_key(self):
        """Test creating a valid API key."""
        key = APIKeyCreate(
            provider="groq",
            api_key="gsk_test_key_123",
            label="My Groq Key",
        )

        assert key.provider == "groq"
        assert key.api_key == "gsk_test_key_123"
        assert key.label == "My Groq Key"

    def test_invalid_provider(self):
        """Test creating with invalid provider."""
        with pytest.raises(ValidationError) as exc_info:
            APIKeyCreate(provider="invalid_provider", api_key="test")

        assert "Unsupported provider" in str(exc_info.value)

    def test_optional_label(self):
        """Test label is optional."""
        key = APIKeyCreate(provider="openai", api_key="sk-test")

        assert key.label is None


class TestAPIKeyResponse:
    """Test API key response model."""

    def test_response_structure(self):
        """Test response has required fields."""
        from datetime import datetime

        response = APIKeyResponse(
            id="123",
            provider="groq",
            masked_key="gsk_...xyz",
            is_valid=True,
            created_at=datetime.now(),
        )

        assert response.id == "123"
        assert response.provider == "groq"
        assert response.masked_key == "gsk_...xyz"
        assert response.is_valid is True
