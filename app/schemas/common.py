"""
SIMORGH Platform API - Common Schemas
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    class Config:
        from_attributes = True


class RequestIdMixin(BaseModel):
    """Mixin for request ID tracking."""
    
    request_id: str = Field(..., description="Unique request identifier")


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginationResponse(BaseModel):
    """Common pagination response metadata."""
    
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    timestamp: datetime


class ReadyResponse(BaseModel):
    """Readiness check response."""
    
    ready: bool
    checks: dict[str, bool] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    code: str
    message: str
    request_id: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "request_id": "req_abc123",
            }
        }
