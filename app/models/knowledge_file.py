"""
SIMORGH Platform API - Knowledge File Model

Represents a file associated with a knowledge document.
Part of the Knowledge Foundation architecture for file storage abstraction.

Supports:
- source tracking
- metadata
- permissions (via tenant/workspace isolation)
- checksum verification
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class KnowledgeFile(Base, UUIDMixin, TimestampMixin):
    """Knowledge file model for storing file metadata."""
    
    __tablename__ = "knowledge_files"
    
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # File metadata
    storage_key = Column(String(255), nullable=False, unique=True, index=True)  # Key in object storage
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)  # Size in bytes
    checksum = Column(String(64), nullable=False)  # SHA256 checksum
    
    # Relationships
    document = relationship("KnowledgeDocument", backref="files")
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_file_tenant', 'tenant_id'),
        Index('ix_file_document', 'document_id'),
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeFile {self.filename} ({self.storage_key})>"
