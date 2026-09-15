"""
SIMORGH Platform API - AI Schemas

Request/response schemas for AI endpoints.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""
    
    role: str = Field(..., description="Role: system, user, assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """AI chat completion request."""
    
    model: str = Field(..., description="Model identifier or routing policy")
    messages: list[Message] = Field(..., description="Conversation messages")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2000, ge=1, le=32000)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Operation metadata (app, operation type, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "reasoning",
                "messages": [
                    {"role": "user", "content": "Analyze this decision."}
                ],
                "temperature": 0.2,
                "max_tokens": 2000,
                "metadata": {
                    "app": "council",
                    "operation": "decision_analysis"
                }
            }
        }


class ChatResponse(BaseModel):
    """AI chat completion response."""
    
    id: str
    model: str
    provider: str
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    request_id: str


class EmbeddingsRequest(BaseModel):
    """Embeddings generation request."""
    
    model: str = Field(..., description="Embedding model")
    input: str | list[str] = Field(..., description="Text to embed")
    metadata: Optional[dict[str, Any]] = None


class EmbeddingsResponse(BaseModel):
    """Embeddings generation response."""
    
    embeddings: list[list[float]]
    model: str
    provider: str
    input_tokens: int
    request_id: str


class ModelInfo(BaseModel):
    """Model information."""
    
    id: str
    name: str
    provider: str
    capabilities: list[str]
    is_available: bool


class ModelsResponse(BaseModel):
    """Available models response."""
    
    models: list[ModelInfo]


class ProviderInfo(BaseModel):
    """Provider information."""
    
    id: str
    name: str
    is_configured: bool
    is_available: bool


class ProvidersResponse(BaseModel):
    """Available providers response."""
    
    providers: list[ProviderInfo]


class UsageEntry(BaseModel):
    """AI usage entry."""
    
    request_id: str
    provider: str
    model: str
    operation: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    status: str
    timestamp: str


class UsageResponse(BaseModel):
    """AI usage history response."""
    
    entries: list[UsageEntry]
    total_requests: int
    total_tokens: int
