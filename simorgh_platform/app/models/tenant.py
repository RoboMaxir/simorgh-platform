"""
SIMORGH Platform API - Tenant Model

Represents a tenant (organization) in the platform.
All multi-tenant resources must be associated with a tenant.
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base, UUIDMixin, TimestampMixin


class Tenant(Base, UUIDMixin, TimestampMixin):
    """Tenant model for multi-tenant isolation."""
    
    __tablename__ = "tenants"
    
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Tenant {self.name} ({self.slug})>"
