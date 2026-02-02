"""Settings and LLM configuration endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.database import get_database
from app.core.deps import get_current_user
from app.models.llm_provider import (
    APIKeyCreate,
    APIKeyResponse,
    LLMConnectionTest,
    LLMProviderInfo,
    LLM_PROVIDERS,
)
from app.models.user import User
from app.repositories.api_key import APIKeyRepository, get_api_key_repository
from app.services.presets import get_all_presets, get_preset_details

router = APIRouter()


@router.get(
    "/llm/providers",
    response_model=list[LLMProviderInfo],
    summary="List LLM providers",
)
async def list_llm_providers(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[LLMProviderInfo]:
    """
    Get list of available LLM providers and their models.
    """
    return list(LLM_PROVIDERS.values())


@router.get(
    "/llm/providers/{provider_id}",
    response_model=LLMProviderInfo,
    summary="Get LLM provider details",
)
async def get_llm_provider(
    provider_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> LLMProviderInfo:
    """
    Get details for a specific LLM provider.
    """
    if provider_id not in LLM_PROVIDERS:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )
    return LLM_PROVIDERS[provider_id]


@router.get(
    "/api-keys",
    response_model=list[APIKeyResponse],
    summary="List API keys",
)
async def list_api_keys(
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_repo: Annotated[APIKeyRepository, Depends(get_api_key_repository)],
) -> list[APIKeyResponse]:
    """
    Get all configured API keys for the current user.

    Keys are returned with masked values for security.
    """
    return await api_key_repo.get_api_keys(current_user.id)


@router.post(
    "/api-keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add API key",
)
async def add_api_key(
    key_data: APIKeyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_repo: Annotated[APIKeyRepository, Depends(get_api_key_repository)],
) -> APIKeyResponse:
    """
    Add or update an API key for a provider.

    The key will be encrypted before storage.
    """
    return await api_key_repo.create_api_key(
        user_id=current_user.id,
        key_data=key_data,
    )


@router.delete(
    "/api-keys/{provider}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete API key",
)
async def delete_api_key(
    provider: str,
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_repo: Annotated[APIKeyRepository, Depends(get_api_key_repository)],
) -> None:
    """
    Delete an API key for a provider.
    """
    await api_key_repo.delete_api_key(current_user.id, provider)


@router.post(
    "/api-keys/{provider}/test",
    response_model=LLMConnectionTest,
    summary="Test API key",
)
async def test_api_key(
    provider: str,
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_repo: Annotated[APIKeyRepository, Depends(get_api_key_repository)],
    db=Depends(get_database),
) -> LLMConnectionTest:
    """
    Test an API key by making a simple request to the provider.
    """
    import time
    from datetime import datetime, timezone

    # Get API key
    api_key = await api_key_repo.get_api_key(current_user.id, provider)
    if not api_key:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key configured for {provider}",
        )

    provider_info = LLM_PROVIDERS.get(provider)
    if not provider_info or not provider_info.models:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider {provider} not supported",
        )

    model = provider_info.models[0].id
    start_time = time.time()
    success = False
    error = None

    try:
        # Test based on provider
        if provider == "groq":
            from groq import AsyncGroq
            client = AsyncGroq(api_key=api_key)
            await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
            success = True
        elif provider == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
            )
            success = True
        elif provider == "anthropic":
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=api_key)
            await client.messages.create(
                model=model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}],
            )
            success = True
        else:
            error = f"Test not implemented for {provider}"

    except Exception as e:
        error = str(e)

    latency_ms = (time.time() - start_time) * 1000

    # Update validation status
    await api_key_repo.update_validation_status(current_user.id, provider, success)

    return LLMConnectionTest(
        provider=provider,
        model=model,
        success=success,
        latency_ms=latency_ms if success else None,
        error=error,
        tested_at=datetime.now(timezone.utc),
    )


@router.get(
    "/presets",
    response_model=list[dict],
    summary="List presets",
)
async def list_presets(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    """
    Get list of available project presets.
    """
    return get_all_presets()


@router.get(
    "/presets/{preset_id}",
    response_model=dict,
    summary="Get preset details",
)
async def get_preset(
    preset_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Get full details for a specific preset including configuration.
    """
    details = get_preset_details(preset_id)
    if not details:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_id}' not found",
        )
    return details
