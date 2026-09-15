"""
SIMORGH Platform API - Knowledge Chunk Model

Represents a chunk of a document with vector embedding.
Used for semantic search via pgvector or other vector stores.
"""
from sqlalchemy import Column, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base, UUIDMixin, TimestampMixin

# Note: Vector type is imported conditionally based on pgvector availability
try:
    from pgvector.sqlalchemy import Vector
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    # Fallback - will raise error if used without pgvector
    Vector = type('Vector', (), {})


class KnowledgeChunk(Base, UUIDMixin, TimestampMixin):
    """Knowledge chunk model with vector embedding."""
    
    __tablename__ = "knowledge_chunks"
    
    document_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    
    # Chunk content
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    
    # Vector embedding (dimension configurable, default 768 for many models)
    embedding = Column(Vector(768), nullable=True)  # Requires pgvector
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_chunk_document', 'document_id', 'chunk_index'),
        Index('ix_chunk_tenant', 'tenant_id'),
        # Note: GIN index on embedding should be created via migration for pgvector
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeChunk doc={self.document_id} idx={self.chunk_index}>"
