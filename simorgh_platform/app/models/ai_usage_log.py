"""
SIMORGH Platform API - AI Usage Log Model

Tracks all AI requests for observability, billing, and analytics.
"""
from sqlalchemy import Column, String, Integer, BigInteger, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base, UUIDMixin, TimestampMixin


class AIUsageLog(Base, UUIDMixin, TimestampMixin):
    """AI usage tracking model."""
    
    __tablename__ = "ai_usage_logs"
    
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    installation_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    credential_id = Column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    request_id = Column(String(64), nullable=False, index=True)
    
    # Provider info
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    logical_model = Column(String(50), nullable=True)  # e.g., "reasoning", "fast"
    operation = Column(String(50), nullable=False)  # "chat", "embeddings"
    
    # Token usage
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Performance
    latency_ms = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, index=True)  # "success", "error"
    error_code = Column(String(50), nullable=True)
    
    # Cost estimation (provider-specific)
    estimated_cost = Column(Float, default=0.0)
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_ai_usage_tenant_created', 'tenant_id', 'created_at'),
        Index('ix_ai_usage_request', 'request_id', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<AIUsageLog {self.request_id} ({self.provider}/{self.model})>"
