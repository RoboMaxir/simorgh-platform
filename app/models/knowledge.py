"""
SIMORGH Platform API - Knowledge Document Model

Foundation for knowledge storage and retrieval.
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

from app.db.base import Base
from app.db.mixins import TimestampMixin


class KnowledgeDocument(Base, TimestampMixin):
    """Knowledge document model."""
    
    __tablename__ = "knowledge_documents"
    
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
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    document_type = Column(String(50), nullable=True)
    metadata = Column(Text, nullable=True)  # JSON metadata
    
    def __repr__(self) -> str:
        return f"<KnowledgeDocument {self.title}>"
