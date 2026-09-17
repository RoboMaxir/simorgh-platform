"""
SIMORGH Platform API - Workspace Model

Represents a workspace within a tenant.
Workspaces provide logical grouping for applications and users.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Workspace(Base, UUIDMixin, TimestampMixin):
    """Workspace model for logical grouping within a tenant."""

    __tablename__ = "workspaces"

    tenant_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    tenant = relationship("Tenant", backref="workspaces")

    # Ensure unique slug per tenant
    __table_args__ = (
        UniqueConstraint('tenant_id', 'slug', name='uq_workspace_tenant_slug'),
    )

    def __repr__(self) -> str:
        return f"<Workspace {self.name} ({self.slug})>"
