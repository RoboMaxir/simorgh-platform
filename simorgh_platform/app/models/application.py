"""
SIMORGH Platform API - Application Model

Represents an application definition (global, not tenant-specific).
Examples: council, product, service, fleet, etc.
Applications are installed into tenants via ApplicationInstallation.
"""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base, UUIDMixin, TimestampMixin


class Application(Base, UUIDMixin, TimestampMixin):
    """Application definition model (global registry)."""
    
    __tablename__ = "applications"
    
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Application {self.name} ({self.slug})>"
