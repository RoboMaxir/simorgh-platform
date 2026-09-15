"""
SIMORGH Platform API - Application Installation Model

Links an Application definition to a Tenant.
This enables the "App Store" model where one application
can be installed by multiple tenants.
"""
from sqlalchemy import Column, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class ApplicationInstallation(Base, UUIDMixin, TimestampMixin):
    """Application installation linking tenant and application."""
    
    __tablename__ = "application_installations"
    
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Composite unique constraint: one installation per app per tenant
    __table_args__ = (
        Index('ix_unique_tenant_app', 'tenant_id', 'application_id', unique=True),
    )
    
    # Relationships
    tenant = relationship("Tenant", backref="installations")
    application = relationship("Application", backref="installations")
    
    def __repr__(self) -> str:
        return f"<ApplicationInstallation tenant={self.tenant_id} app={self.application_id}>"
