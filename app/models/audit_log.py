"""
SIMORGH Platform API - Audit Log Model

Immutable audit trail for platform operations.
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import uuid

from app.db.base import Base
from app.db.mixins import TimestampMixin


class AuditLog(Base, TimestampMixin):
    """Audit log model for tracking platform operations."""
    
    __tablename__ = "audit_logs"
    
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
    actor_id = Column(String(255), nullable=True)  # User or service ID
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(64), nullable=True)
    request_id = Column(String(64), nullable=False, index=True)
    metadata = Column(JSONB, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.resource}>"
