"""SIMORGH Platform SDK - AI client."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Chat message for AI conversations."""
    role: str
    content: str


@dataclass
class ChatResponse:
    """Chat completion response."""
    id: str
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    request_id: str


@dataclass
class EmbeddingsResponse:
    """Embeddings generation response."""
    embeddings: List[List[float]]
    model: str
    provider: str
    input_tokens: int
    request_id: str


class AIClient:
    """AI client for chat and embeddings operations."""
    
    def __init__(self, http_client):
        self._http = http_client
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "reasoning",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier or routing policy (e.g., 'reasoning', 'fast', 'gpt-4')
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            metadata: Optional metadata for tracking
            
        Returns:
            ChatResponse with completion content and usage info
        """
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        if metadata:
            payload["metadata"] = metadata
        
        response = await self._http.post("/ai/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return ChatResponse(
            id=data["id"],
            content=data["content"],
            model=data["model"],
            provider=data["provider"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            total_tokens=data["total_tokens"],
            request_id=data["request_id"],
        )
    
    async def embedding(
        self,
        text: str | List[str],
        model: str = "text-embedding-3-small",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmbeddingsResponse:
        """Generate embeddings for text.
        
        Args:
            text: Single text string or list of strings to embed
            model: Embedding model identifier
            metadata: Optional metadata for tracking
            
        Returns:
            EmbeddingsResponse with embedding vectors
        """
        payload = {
            "input": text,
            "model": model,
        }
        if metadata:
            payload["metadata"] = metadata
        
        response = await self._http.post("/ai/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return EmbeddingsResponse(
            embeddings=data["embeddings"],
            model=data["model"],
            provider=data["provider"],
            input_tokens=data["input_tokens"],
            request_id=data["request_id"],
        )
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available AI models.
        
        Returns:
            List of model dictionaries with id, name, provider, capabilities
        """
        response = await self._http.get("/ai/models")
        response.raise_for_status()
        data = response.json()
        return data.get("models", [])
    
    async def list_providers(self) -> List[Dict[str, Any]]:
        """List all configured AI providers.
        
        Returns:
            List of provider dictionaries with id, name, availability status
        """
        response = await self._http.get("/ai/providers")
        response.raise_for_status()
        return response.json().get("providers", [])
