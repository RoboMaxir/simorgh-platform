"""
SIMORGH Platform API - Knowledge Document Model

Represents a document in the knowledge base.
Part of the Knowledge Foundation architecture:

KnowledgeSpace
    |
    Document
        |
        Chunk
            |
            Embedding

Supports:
- source tracking
- metadata
- permissions
"""
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class KnowledgeDocument(Base, UUIDMixin, TimestampMixin):
    """Knowledge document model."""
    
    __tablename__ = "knowledge_documents"
    
    space_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_spaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Document metadata
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)  # URL, file path, etc.
    mime_type = Column(String(100), default="text/plain")
    
    # Indexing status
    is_indexed = Column(Boolean, default=False, index=True)
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional metadata
    metadata_json = Column(JSONB, nullable=True)
    
    # Relationships
    space = relationship("KnowledgeSpace", back_populates="documents")
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_knowledge_tenant_source', 'tenant_id', 'source'),
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeDocument {self.title}>"
