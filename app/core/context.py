"""
SIMORGH Platform API - Request Context

Provides request-scoped context including tenant, application, and auth info.
"""
from dataclasses import dataclass
from typing import List, Optional
import uuid


@dataclass
class RequestContext:
    """Request context containing authenticated identity and metadata."""
    
    request_id: str
    tenant_id: str
    application_id: str
    installation_id: str
    credential_id: str
    scopes: List[str]
    
    @classmethod
    def from_token_payload(cls, payload: dict, request_id: Optional[str] = None) -> "RequestContext":
        """Create context from JWT token payload."""
        return cls(
            request_id=request_id or str(uuid.uuid4()),
            tenant_id=payload["tenant_id"],
            application_id=payload["application_id"],
            installation_id=payload["installation_id"],
            credential_id=payload.get("credential_id"),
            scopes=payload.get("scopes", []),
        )
    
    def has_scope(self, required_scope: str) -> bool:
        """Check if context has a required scope."""
        if not self.scopes:
            return False
        return required_scope in self.scopes or "*" in self.scopes
