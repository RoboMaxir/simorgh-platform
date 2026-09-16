"""
SIMORGH Platform API - OpenAI-Compatible Provider

Provider for local or custom OpenAI-compatible endpoints.
"""
import time
from typing import Any, Optional

import httpx

from app.providers.base import AIProvider, ChatMessage, ChatResponse, EmbeddingsResponse
from app.config import get_settings
from app.core.exceptions import ProviderConfigurationError, AIProviderError


settings = get_settings()


class OpenAICompatibleProvider(AIProvider):
    """OpenAI-compatible API provider for local/custom endpoints."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self._base_url = base_url or settings.local_llm_endpoint
        self._api_key = api_key or "not-needed"  # Many local models don't require keys
        self._timeout = 60.0  # Longer timeout for local models
    
    @property
    def provider_id(self) -> str:
        return "openai_compatible"
    
    @property
    def provider_name(self) -> str:
        return "OpenAI Compatible (Local)"
    
    async def is_available(self) -> bool:
        if not self._base_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/models")
                return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> list[dict[str, Any]]:
        if not await self.is_available():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._base_url}/models")
                response.raise_for_status()
                data = response.json()
                
                return [
                    {
                        "id": model.get("id", model.get("name", "unknown")),
                        "name": model.get("name", model.get("id", "unknown")),
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
        if not await self.is_available():
            raise ProviderConfigurationError("OpenAI-compatible endpoint is not available")
        
        start_time = time.time()
        
        try:
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
            
            headers = {
                "Content-Type": "application/json",
            }
            
            if self._api_key and self._api_key != "not-needed":
                headers["Authorization"] = f"Bearer {self._api_key}"
            
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/v1/chat/completions",
                    headers=headers,
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
            raise AIProviderError(f"OpenAI-compatible API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"OpenAI-compatible request failed: {str(e)}")
    
    async def embeddings(
        self,
        input_text: str | list[str],
        model: str,
        **kwargs: Any,
    ) -> EmbeddingsResponse:
        if not await self.is_available():
            raise ProviderConfigurationError("OpenAI-compatible endpoint is not available")
        
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "input": input_text,
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            if self._api_key and self._api_key != "not-needed":
                headers["Authorization"] = f"Bearer {self._api_key}"
            
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/v1/embeddings",
                    headers=headers,
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
            raise AIProviderError(f"OpenAI-compatible API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"OpenAI-compatible embeddings request failed: {str(e)}")
