"""
SIMORGH Platform API - Audit Event Model

Append-only audit log for platform events.
Records who did what, when, and in which context.
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB

from app.models.base import Base, UUIDMixin, TimestampMixin


class AuditEvent(Base, UUIDMixin, TimestampMixin):
    """Audit event model for tracking platform actions."""
    
    __tablename__ = "audit_events"
    
    # Context (from authenticated request, never trusted from input)
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
    )
    request_id = Column(String(64), nullable=False, index=True)
    
    # Actor information
    actor_type = Column(String(20), nullable=False)  # "service", "user"
    actor_id = Column(String(255), nullable=True)  # Service/app ID or user ID
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_audit_tenant_created', 'tenant_id', 'created_at'),
        Index('ix_audit_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self) -> str:
        return f"<AuditEvent {self.action} by {self.actor_id}>"
