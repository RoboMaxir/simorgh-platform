"""
SIMORGH Platform API - OpenAI Provider

OpenAI API provider implementation.
"""
import time
from typing import Any, Optional

import httpx

from app.providers.base import AIProvider, ChatMessage, ChatResponse, EmbeddingsResponse
from app.config import get_settings
from app.core.exceptions import ProviderConfigurationError, AIProviderError


settings = get_settings()


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self):
        self._api_key: Optional[str] = settings.openai_api_key
        self._base_url = "https://api.openai.com/v1"
        self._timeout = 30.0
    
    @property
    def provider_id(self) -> str:
        return "openai"
    
    @property
    def provider_name(self) -> str:
        return "OpenAI"
    
    async def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return self._api_key is not None and len(self._api_key) > 0
    
    async def list_models(self) -> list[dict[str, Any]]:
        """List available OpenAI models."""
        if not await self.is_available():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/models",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                response.raise_for_status()
                data = response.json()
                
                return [
                    {
                        "id": model["id"],
                        "name": model["id"],
                        "provider": self.provider_id,
                        "capabilities": ["chat"],
                        "is_available": True,
                    }
                    for model in data.get("data", [])
                ]
        except Exception:
            return []
    
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat completion request to OpenAI."""
        if not await self.is_available():
            raise ProviderConfigurationError("OpenAI is not configured")
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": msg.role, "content": msg.content}
                        for msg in messages
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                }
                
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                choice = data["choices"][0]
                usage = data.get("usage", {})
                latency_ms = int((time.time() - start_time) * 1000)
                
                return ChatResponse(
                    content=choice["message"]["content"],
                    model=model,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    latency_ms=latency_ms,
                    raw_response=data,
                )
        except httpx.HTTPStatusError as e:
            raise AIProviderError(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"OpenAI request failed: {str(e)}")
    
    async def embeddings(
        self,
        input_text: str | list[str],
        model: str,
        **kwargs: Any,
    ) -> EmbeddingsResponse:
        """Generate embeddings using OpenAI."""
        if not await self.is_available():
            raise ProviderConfigurationError("OpenAI is not configured")
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                payload = {
                    "model": model,
                    "input": input_text,
                }
                
                response = await client.post(
                    f"{self._base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                usage = data.get("usage", {})
                latency_ms = int((time.time() - start_time) * 1000)
                
                embeddings = [item["embedding"] for item in data["data"]]
                
                return EmbeddingsResponse(
                    embeddings=embeddings,
                    model=model,
                    input_tokens=usage.get("prompt_tokens", 0),
                    latency_ms=latency_ms,
                )
        except httpx.HTTPStatusError as e:
            raise AIProviderError(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"OpenAI embeddings request failed: {str(e)}")
