"""Canonical ORM model registry used by Alembic."""
from app.models.application import Application
from app.models.application_installation import ApplicationInstallation
from app.models.audit_event import AuditEvent
from app.models.ai_usage import AIUsage
from app.models.credential import Credential
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.tenant import Tenant

__all__ = [
    "Application",
    "ApplicationInstallation",
    "AuditEvent",
    "AIUsage",
    "Credential",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "Tenant",
]
