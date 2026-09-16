"""
SIMORGH Platform API - Credential Model

Stores hashed secrets for application authentication.
Credentials belong to an ApplicationInstallation (tenant-specific).
Supports scope-based authorization.
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.models.base import Base, UUIDMixin, TimestampMixin


class Credential(Base, UUIDMixin, TimestampMixin):
    """Credential model for application authentication."""
    
    __tablename__ = "credentials"
    
    installation_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("application_installations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key_id = Column(String(64), nullable=False, index=True)  # Public identifier
    secret_hash = Column(String(255), nullable=False)  # Argon2 hash
    name = Column(String(100), nullable=False)
    scopes = Column(Text, nullable=True)  # JSON array of scopes as text
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(
        TimestampMixin.created_at.__class__,
        nullable=True,
    )
    last_used_at = Column(
        TimestampMixin.created_at.__class__,
        nullable=True,
    )
    
    # Relationships
    installation = relationship("ApplicationInstallation", backref="credentials")
    
    def __repr__(self) -> str:
        return f"<Credential {self.key_id} ({self.name})>"
    
    def has_scope(self, scope: str) -> bool:
        """Check if credential has a specific scope."""
        if not self.scopes:
            return False
        import json
        try:
            scopes_list = json.loads(self.scopes)
            return scope in scopes_list or "*" in scopes_list
        except (json.JSONDecodeError, TypeError):
            return False
    
    def is_expired(self) -> bool:
        """Check if credential has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
