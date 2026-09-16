"""
SIMORGH Platform API - Common Model Mixins
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TenantMixin:
    """Mixin for tenant ownership - ensures multi-tenant isolation."""
    
    tenant_id = Column(
        String(36),
        nullable=False,
        index=True,
    )
    
    @classmethod
    def __declare_last__(cls):
        """Create composite index for tenant isolation."""
        pass


class UUIDPrimaryKeyMixin:
    """Mixin for UUID primary keys."""
    
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
