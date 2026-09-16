"""
SIMORGH Platform API - Event Model

Platform events for async communication and auditing.
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import uuid

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Event(Base, TimestampMixin):
    """Event model for platform events."""
    
    __tablename__ = "events"
    
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
    event_name = Column(String(100), nullable=False, index=True)
    actor_id = Column(String(255), nullable=True)
    payload = Column(JSONB, nullable=True)
    request_id = Column(String(64), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Event {self.event_name}>"
