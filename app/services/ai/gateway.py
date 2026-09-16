"""
SIMORGH Platform API - AI Gateway

Central gateway for all AI operations.
Routes requests to appropriate providers and tracks usage.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import AIProvider, ChatMessage, ChatResponse, EmbeddingsResponse
from app.services.ai.router import ModelRouter
from app.services.ai.usage import UsageTracker
from app.core.exceptions import (
    ProviderUnavailableError,
    AIProviderError,
    ProviderConfigurationError,
)
from app.core.logging import get_logger


logger = get_logger(__name__)


class AIGateway:
    """Central AI gateway for all AI operations."""
    
    def __init__(
        self,
        db_session: AsyncSession,
        providers: dict[str, AIProvider],
    ):
        self.db = db_session
        self.providers = providers
        self.router = ModelRouter(providers)
        self.usage_tracker = UsageTracker(db_session)
    
    async def chat(
        self,
        tenant_id: str,
        application_id: Optional[str],
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ChatResponse:
        """Process a chat completion request."""
        
        request_id = str(uuid.uuid4())
        operation = (metadata or {}).get("operation", "chat")
        
        logger.info(
            "ai_chat_request",
            request_id=request_id,
            tenant_id=tenant_id,
            model=model,
            operation=operation,
        )
        
        try:
            # Resolve model to provider
            provider_id, resolved_model = await self.router.resolve_model(model)
            
            provider = self.providers.get(provider_id)
            if not provider:
                raise ProviderUnavailableError(f"Provider {provider_id} not found")
            
            # Convert messages to internal format
            chat_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            
            # Call provider
            response = await provider.chat(
                messages=chat_messages,
                model=resolved_model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )
            
            # Record usage
            await self.usage_tracker.record_usage(
                tenant_id=tenant_id,
                application_id=application_id,
                request_id=request_id,
                provider=provider_id,
                model=resolved_model,
                operation=operation,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                total_tokens=response.total_tokens,
                latency_ms=response.latency_ms,
                status="success",
                metadata=metadata,
            )
            
            logger.info(
                "ai_chat_success",
                request_id=request_id,
                provider=provider_id,
                model=resolved_model,
                tokens=response.total_tokens,
            )
            
            # Add request_id to response
            response.request_id = request_id
            
            return response
            
        except (ProviderUnavailableError, ProviderConfigurationError, AIProviderError):
            raise
        except Exception as e:
            logger.error(
                "ai_chat_error",
                request_id=request_id,
                error=str(e),
            )
            
            # Record failed usage
            await self.usage_tracker.record_usage(
                tenant_id=tenant_id,
                application_id=application_id,
                request_id=request_id,
                provider="unknown",
                model=model,
                operation=operation,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=0,
                status="error",
                error_message=str(e),
                metadata=metadata,
            )
            
            raise AIProviderError(f"Chat completion failed: {str(e)}")
    
    async def embeddings(
        self,
        tenant_id: str,
        application_id: Optional[str],
        input_text: str | list[str],
        model: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> EmbeddingsResponse:
        """Process an embeddings request."""
        
        request_id = str(uuid.uuid4())
        
        logger.info(
            "ai_embeddings_request",
            request_id=request_id,
            tenant_id=tenant_id,
            model=model,
        )
        
        try:
            # Resolve model to provider
            provider_id, resolved_model = await self.router.resolve_model(model)
            
            provider = self.providers.get(provider_id)
            if not provider:
                raise ProviderUnavailableError(f"Provider {provider_id} not found")
            
            # Call provider
            response = await provider.embeddings(
                input_text=input_text,
                model=resolved_model,
            )
            
            # Record usage
            await self.usage_tracker.record_usage(
                tenant_id=tenant_id,
                application_id=application_id,
                request_id=request_id,
                provider=provider_id,
                model=resolved_model,
                operation="embeddings",
                input_tokens=response.input_tokens,
                output_tokens=0,
                total_tokens=response.input_tokens,
                latency_ms=response.latency_ms,
                status="success",
                metadata=metadata,
            )
            
            logger.info(
                "ai_embeddings_success",
                request_id=request_id,
                provider=provider_id,
                tokens=response.input_tokens,
            )
            
            # Add request_id to response
            response.request_id = request_id
            
            return response
            
        except Exception as e:
            logger.error(
                "ai_embeddings_error",
                request_id=request_id,
                error=str(e),
            )
            raise AIProviderError(f"Embeddings generation failed: {str(e)}")
    
    async def list_models(self) -> list[dict[str, Any]]:
        """List all available models from all providers."""
        all_models = []
        
        for provider_id, provider in self.providers.items():
            if await provider.is_available():
                models = await provider.list_models()
                all_models.extend(models)
        
        return all_models
    
    async def list_providers(self) -> list[dict[str, Any]]:
        """List all configured providers with availability status."""
        providers_info = []
        
        for provider_id, provider in self.providers.items():
            is_available = await provider.is_available()
            providers_info.append({
                "id": provider_id,
                "name": provider.provider_name,
                "is_configured": is_available,
                "is_available": is_available,
            })
        
        return providers_info
