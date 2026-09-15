"""
SIMORGH Platform API - AI Provider Base Interface

Abstract base class for all AI providers.
"""
from typing import List, Dict, Any, Optional


class ChatMessage:
    """Standardized chat message."""
    
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class ChatResponse:
    """Standardized chat response."""
    
    def __init__(
        self,
        content: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        finish_reason: Optional[str] = None,
        latency_ms: Optional[int] = None,
    ):
        self.content = content
        self.model = model
        self.provider = provider
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.finish_reason = finish_reason
        self.latency_ms = latency_ms


class EmbeddingsResponse:
    """Standardized embeddings response."""
    
    def __init__(
        self,
        embeddings: List[List[float]],
        model: str,
        provider: str,
        total_tokens: int,
        latency_ms: Optional[int] = None,
    ):
        self.embeddings = embeddings
        self.model = model
        self.provider = provider
        self.total_tokens = total_tokens
        self.latency_ms = latency_ms


class ModelInfo:
    """Model information."""
    
    def __init__(self, id: str, name: str, provider: str, capabilities: List[str]):
        self.id = id
        self.name = name
        self.provider = provider
        self.capabilities = capabilities


class AIProvider:
    """Abstract base class for AI providers."""
    
    @property
    def name(self) -> str:
        """Provider name identifier."""
        pass
    
    @property
    def provider_type(self) -> str:
        """Provider type (e.g., 'openai-compatible', 'anthropic')."""
        pass
    
    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatResponse:
        """Send chat completion request."""
        pass
    
    async def embeddings(
        self,
        texts: List[str],
        model: str,
        **kwargs,
    ) -> EmbeddingsResponse:
        """Generate embeddings for texts."""
        pass
    
    async def list_models(self) -> List[ModelInfo]:
        """List available models from this provider."""
        pass
    
    async def is_available(self) -> bool:
        """Check if provider is available."""
        pass
