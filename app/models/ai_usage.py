"""
SIMORGH Platform API - AI Usage Tracking Model

Tracks all AI requests for usage monitoring, billing, and analytics.
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from datetime import datetime, timezone

from app.models.base import Base


class AIUsage(Base):
    """AI Usage tracking model."""

    __tablename__ = "ai_usage"

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    request_id = Column(String(64), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    operation = Column(String(50), nullable=False)  # chat, embeddings, etc.
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)  # success, error
    error_message = Column(Text, nullable=True)
    estimated_cost = Column(Float, default=0.0)
    metadata_json = Column(Text, nullable=True)  # JSON metadata
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AIUsage {self.request_id} ({self.provider}/{self.model})>"
