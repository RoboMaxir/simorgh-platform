"""
SIMORGH Platform API - Qwen Provider

Qwen-compatible API provider implementation.
"""
import time
from typing import Any, Optional

import httpx

from app.providers.base import AIProvider, ChatMessage, ChatResponse, EmbeddingsResponse
from app.config import get_settings
from app.core.exceptions import ProviderConfigurationError, AIProviderError


settings = get_settings()


class QwenProvider(AIProvider):
    """Qwen API provider."""
    
    def __init__(self):
        self._api_key: Optional[str] = settings.qwen_api_key
        # Default to Alibaba Cloud endpoint
        self._base_url = "https://dashscope.aliyuncs.com/api/v1"
        self._timeout = 30.0
    
    @property
    def provider_id(self) -> str:
        return "qwen"
    
    @property
    def provider_name(self) -> str:
        return "Qwen"
    
    async def is_available(self) -> bool:
        return self._api_key is not None and len(self._api_key) > 0
    
    async def list_models(self) -> list[dict[str, Any]]:
        if not await self.is_available():
            return []
        
        return [
            {
                "id": "qwen-turbo",
                "name": "Qwen Turbo",
                "provider": self.provider_id,
                "capabilities": ["chat", "fast"],
                "is_available": True,
            },
            {
                "id": "qwen-plus",
                "name": "Qwen Plus",
                "provider": self.provider_id,
                "capabilities": ["chat", "reasoning"],
                "is_available": True,
            },
            {
                "id": "qwen-max",
                "name": "Qwen Max",
                "provider": self.provider_id,
                "capabilities": ["chat", "reasoning"],
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
            raise ProviderConfigurationError("Qwen is not configured")
        
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {"role": msg.role, "content": msg.content}
                        for msg in messages
                    ]
                },
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                output = data.get("output", {})
                usage = data.get("usage", {})
                latency_ms = int((time.time() - start_time) * 1000)
                
                return ChatResponse(
                    content=output.get("text", ""),
                    model=model,
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    latency_ms=latency_ms,
                    raw_response=data,
                )
        except httpx.HTTPStatusError as e:
            raise AIProviderError(f"Qwen API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"Qwen request failed: {str(e)}")
    
    async def embeddings(
        self,
        input_text: str | list[str],
        model: str,
        **kwargs: Any,
    ) -> EmbeddingsResponse:
        if not await self.is_available():
            raise ProviderConfigurationError("Qwen is not configured")
        
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "input": {"texts": input_text if isinstance(input_text, list) else [input_text]},
            }
            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/services/embeddings/text-embedding/generation",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                usage = data.get("usage", {})
                latency_ms = int((time.time() - start_time) * 1000)
                
                embeddings = [item["embedding"] for item in data.get("output", {}).get("embeddings", [])]
                
                return EmbeddingsResponse(
                    embeddings=embeddings,
                    model=model,
                    input_tokens=usage.get("total_tokens", 0),
                    latency_ms=latency_ms,
                )
        except httpx.HTTPStatusError as e:
            raise AIProviderError(f"Qwen API error: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"Qwen embeddings request failed: {str(e)}")
