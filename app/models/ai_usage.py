"""
SIMORGH Platform API - AI Usage Tracking Model

Tracks all AI requests for usage monitoring, billing, and analytics.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

from app.models.base import Base, TimestampMixin


class AIUsage(Base, TimestampMixin):
    """AI Usage tracking model."""
    
    __tablename__ = "ai_usage"
    
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    tenant_id = Column(
        String(36),
        nullable=False,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    installation_id = Column(PG_UUID(as_uuid=True), ForeignKey("application_installations.id", ondelete="SET NULL"), nullable=True, index=True)
    request_id = Column(String(64), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    logical_model = Column(String(100), nullable=False)
    operation = Column(String(50), nullable=False)  # chat, embeddings, etc.
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)  # success, error
    error_message = Column(Text, nullable=True)
    estimated_cost = Column(Float, default=0.0)
    metadata = Column(Text, nullable=True)  # JSON metadata
    
    def __repr__(self) -> str:
        return f"<AIUsage {self.request_id} ({self.provider}/{self.model})>"
