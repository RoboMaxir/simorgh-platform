"""
SIMORGH Platform API - Knowledge Embedding Model

Represents a vector embedding for a knowledge chunk.
Part of the Knowledge Foundation architecture:

KnowledgeSpace
    |
    Document
        |
        Chunk
            |
            Embedding

Supports:
- source tracking (via chunk/document)
- metadata
- permissions (via tenant/workspace isolation)
"""
from sqlalchemy import Column, Integer, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class KnowledgeEmbedding(Base, UUIDMixin, TimestampMixin):
    """Knowledge embedding model for storing vector embeddings."""
    
    __tablename__ = "knowledge_embeddings"
    
    chunk_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("knowledge_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
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
    
    # Embedding metadata
    embedding_model = Column(String(100), nullable=False)  # e.g., "text-embedding-ada-002"
    dimensions = Column(Integer, nullable=False)  # e.g., 768, 1536
    
    # Relationships
    chunk = relationship("KnowledgeChunk", back_populates="embeddings")
    
    # Composite index for common queries
    __table_args__ = (
        Index('ix_embedding_tenant', 'tenant_id'),
        Index('ix_embedding_model', 'embedding_model'),
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeEmbedding chunk={self.chunk_id} model={self.embedding_model}>"
