"""
SIMORGH Platform API - Knowledge Space Model

Logical grouping for knowledge documents.
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
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class KnowledgeSpace(Base, UUIDMixin, TimestampMixin):
    """Knowledge space for organizing documents."""

    __tablename__ = "knowledge_spaces"

    workspace_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)  # Visible to all workspace members
    metadata_json = Column(JSONB, nullable=True)

    # Relationships
    workspace = relationship("Workspace", backref="knowledge_spaces")
    tenant = relationship("Tenant", backref="knowledge_spaces")
    documents = relationship("KnowledgeDocument", back_populates="space", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<KnowledgeSpace {self.name}>"
