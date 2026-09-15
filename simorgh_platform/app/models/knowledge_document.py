"""
SIMORGH Platform API - Knowledge Document Model

Represents a document in the knowledge base.
Documents can be chunked for vector search.
"""
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB

from app.models.base import Base, UUIDMixin, TimestampMixin


class KnowledgeDocument(Base, UUIDMixin, TimestampMixin):
    """Knowledge document model."""
    
    __tablename__ = "knowledge_documents"
    
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    application_id = Column(
        PG_UUID(as_uuid=True),
        nullable=True,  # Can be null for global knowledge
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
    metadata = Column(JSONB, nullable=True)
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_knowledge_tenant_source', 'tenant_id', 'source'),
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeDocument {self.title}>"
