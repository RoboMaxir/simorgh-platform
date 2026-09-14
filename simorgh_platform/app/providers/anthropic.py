"""
SIMORGH Platform API - Anthropic Provider

Anthropic Claude API provider implementation.
"""
import time
from typing import Any, Optional

import httpx

from app.providers.base import AIProvider, ChatMessage, ChatResponse, EmbeddingsResponse
from app.config import get_settings
from app.core.exceptions import ProviderConfigurationError, AIProviderError


settings = get_settings()


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self):
        self._api_key: Optional[str] = settings.anthropic_api_key
        self._base_url = "https://api.anthropic.com/v1"
        self._timeout = 30.0
    
    @property
    def provider_id(self) -> str:
        return "anthropic"
    
    @property
    def provider_name(self) -> str:
        return "Anthropic"
    
    async def is_available(self) -> bool:
        return self._api_key is not None and len(self._api_key) > 0
    
    async def list_models(self) -> list[dict[str, Any]]:
        if not await self.is_available():
            return []
        
        # Return known Claude models
        return [
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "provider": self.provider_id,
                "capabilities": ["chat", "reasoning"],
                "is_available": True,
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "provider": self.provider_id,
                "capabilities": ["chat", "reasoning"],
                "is_available": True,
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "provider": self.provider_id,
                "capabilities": ["chat", "fast"],
                "is_available": True,
            },
        ]
    
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        **kwargs: Any,
    ) -> ChatResponse:
        if not await self.is_available():
            raise ProviderConfigurationError("Anthropic is not configured")
        
        start_time = time.time()
        
        try:
            # Convert messages to Anthropic format
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                    })
            
            payload = {
                "model": model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            
            if system_message:
                payload["system"] = system_message
            
            headers = {
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/messages",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["content"][0]["text"]
                usage = data.get("usage", {})
                latency_ms = int((time.time() - start_time) * 1000)
                
                return ChatResponse(
                    content=content,
                    model=model,
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                    latency_ms=latency_ms,
                    raw_response=data,
                )
        except httpx.HTTPStatusError as e:
            raise AIProviderError(f"Anthropic API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"Anthropic request failed: {str(e)}")
    
    async def embeddings(
        self,
        input_text: str | list[str],
        model: str,
        **kwargs: Any,
    ) -> EmbeddingsResponse:
        # Anthropic doesn't provide embeddings API
        raise AIProviderError("Anthropic does not support embeddings")
