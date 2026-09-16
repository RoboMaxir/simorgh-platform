"""
SIMORGH Platform API - AI Endpoints

AI Gateway endpoints for chat, embeddings, models, and usage.
"""
from typing import Annotated
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_context, get_db
from app.db.base import async_session_maker
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    EmbeddingsRequest,
    EmbeddingsResponse,
    ModelsResponse,
    ProvidersResponse,
    UsageResponse,
    UsageEntry,
)
from app.core.exceptions import PlatformException
from app.core.logging import get_logger


logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    context: Annotated[dict, Depends(get_context)],
):
    """
    Send a chat completion request.
    
    Applications should use model identifiers or routing policies
    instead of provider-specific model names.
    """
    from app.services.ai.gateway import AIGateway
    from app.providers.openai import OpenAIProvider
    from app.providers.anthropic import AnthropicProvider
    from app.providers.qwen import QwenProvider
    from app.providers.openai_compatible import OpenAICompatibleProvider
    
    async with async_session_maker() as session:
        providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "qwen": QwenProvider(),
            "openai_compatible": OpenAICompatibleProvider(),
        }
        
        gateway = AIGateway(db_session=session, providers=providers)
        
        try:
            response = await gateway.chat(
                tenant_id=context["tenant_id"],
                application_id=context["application_id"],
                messages=[msg.model_dump() for msg in request.messages],
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                metadata=request.metadata,
            )
            
            return ChatResponse(
                id=response.request_id,
                model=response.model,
                provider=str(type(response.raw_response).__module__),
                content=response.content,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                total_tokens=response.total_tokens,
                latency_ms=response.latency_ms,
                request_id=response.request_id,
            )
        except PlatformException:
            raise
        except Exception as e:
            logger.error("chat_error", error=str(e), context=context)
            raise HTTPException(status_code=502, detail=str(e))


@router.post("/embeddings", response_model=EmbeddingsResponse)
async def embeddings(
    request: EmbeddingsRequest,
    context: Annotated[dict, Depends(get_context)],
):
    """Generate embeddings for text."""
    from app.services.ai.gateway import AIGateway
    from app.providers.openai import OpenAIProvider
    from app.providers.qwen import QwenProvider
    from app.providers.openai_compatible import OpenAICompatibleProvider
    
    async with async_session_maker() as session:
        providers = {
            "openai": OpenAIProvider(),
            "qwen": QwenProvider(),
            "openai_compatible": OpenAICompatibleProvider(),
        }
        
        gateway = AIGateway(db_session=session, providers=providers)
        
        try:
            response = await gateway.embeddings(
                tenant_id=context["tenant_id"],
                application_id=context["application_id"],
                input_text=request.input,
                model=request.model,
                metadata=request.metadata,
            )
            
            return EmbeddingsResponse(
                embeddings=response.embeddings,
                model=response.model,
                provider=str(type(response).__module__),
                input_tokens=response.input_tokens,
                request_id=response.request_id,
            )
        except PlatformException:
            raise
        except Exception as e:
            logger.error("embeddings_error", error=str(e), context=context)
            raise HTTPException(status_code=502, detail=str(e))


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """List all available AI models."""
    from app.providers.openai import OpenAIProvider
    from app.providers.anthropic import AnthropicProvider
    from app.providers.qwen import QwenProvider
    from app.providers.openai_compatible import OpenAICompatibleProvider
    
    providers = {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "qwen": QwenProvider(),
        "openai_compatible": OpenAICompatibleProvider(),
    }
    
    all_models = []
    for provider in providers.values():
        if await provider.is_available():
            models = await provider.list_models()
            all_models.extend(models)
    
    return ModelsResponse(models=all_models)


@router.get("/providers", response_model=ProvidersResponse)
async def list_providers():
    """List all configured AI providers."""
    from app.providers.openai import OpenAIProvider
    from app.providers.anthropic import AnthropicProvider
    from app.providers.qwen import QwenProvider
    from app.providers.openai_compatible import OpenAICompatibleProvider
    
    providers = {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "qwen": QwenProvider(),
        "openai_compatible": OpenAICompatibleProvider(),
    }
    
    providers_info = []
    for provider_id, provider in providers.items():
        is_available = await provider.is_available()
        providers_info.append({
            "id": provider_id,
            "name": provider.provider_name,
            "is_configured": is_available,
            "is_available": is_available,
        })
    
    return ProvidersResponse(providers=providers_info)


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    context: Annotated[dict, Depends(get_context)],
):
    """Get AI usage history for the current tenant."""
    from app.services.ai.usage import UsageTracker
    
    async with async_session_maker() as session:
        tracker = UsageTracker(session)
        usage_entries = await tracker.get_usage(context["tenant_id"])
        summary = await tracker.get_usage_summary(context["tenant_id"])
        
        return UsageResponse(
            entries=[
                UsageEntry(
                    request_id=e.request_id,
                    provider=e.provider,
                    model=e.model,
                    operation=e.operation,
                    input_tokens=e.input_tokens,
                    output_tokens=e.output_tokens,
                    total_tokens=e.total_tokens,
                    status=e.status,
                    timestamp=e.created_at.isoformat() if e.created_at else "",
                )
                for e in usage_entries
            ],
            total_requests=summary["total_requests"],
            total_tokens=summary["total_tokens"],
        )
