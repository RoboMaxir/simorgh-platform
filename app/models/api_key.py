"""
SIMORGH Platform API - API Key Model

Stores hashed API keys for application authentication.
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

from app.db.base import Base
from app.db.mixins import TimestampMixin


class APIKey(Base, TimestampMixin):
    """API Key model for application authentication."""
    
    __tablename__ = "api_keys"
    
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    key_hash = Column(String(64), nullable=False, index=True)
    scopes = Column(Text, nullable=True)  # JSON array of scopes as text
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(
        TimestampMixin.created_at.__class__,
        nullable=True,
    )
    
    def __repr__(self) -> str:
        return f"<APIKey {self.name}>"
