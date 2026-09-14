"""
SIMORGH Platform API - Application Model

Represents an application that consumes platform services.
Examples: council, product, service, fleet, etc.
"""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Application(Base, TimestampMixin):
    """Application identity model."""
    
    __tablename__ = "applications"
    
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
    name = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Application {self.name} ({self.slug})>"
