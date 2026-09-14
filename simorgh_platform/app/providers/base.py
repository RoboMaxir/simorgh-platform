"""
SIMORGH Platform API - AI Provider Base Interface

Abstract base class for all AI provider implementations.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Chat message for provider communication."""
    role: str
    content: str


@dataclass
class ChatResponse:
    """Standardized chat response from provider."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    raw_response: Any


@dataclass
class EmbeddingsResponse:
    """Standardized embeddings response from provider."""
    embeddings: list[list[float]]
    model: str
    input_tokens: int
    latency_ms: int


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return unique provider identifier."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return human-readable provider name."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass
    
    @abstractmethod
    async def list_models(self) -> list[dict[str, Any]]:
        """List available models from this provider."""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat completion request."""
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        input_text: str | list[str],
        model: str,
        **kwargs: Any,
    ) -> EmbeddingsResponse:
        """Generate embeddings for text."""
        pass
