"""
SIMORGH Platform API - API Dependencies

Common dependencies for API endpoints.
"""
import uuid
from typing import Optional, Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import decode_access_token, verify_scope
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    TenantIsolationError,
)
from app.core.logging import get_logger


logger = get_logger(__name__)


async def get_request_id(x_request_id: Optional[str] = Header(None)) -> str:
    """Get or generate request ID for tracing."""
    return x_request_id or str(uuid.uuid4())


async def get_auth_context(
    authorization: Optional[str] = Header(None),
) -> dict:
    """Extract and validate authentication context from request."""
    if not authorization:
        raise AuthenticationError("Missing authorization header")
    
    try:
        # Support Bearer token format
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
        
        payload = decode_access_token(token)
        
        return {
            "subject": payload.get("sub"),
            "tenant_id": payload.get("tenant_id"),
            "application_id": payload.get("application_id"),
            "scopes": payload.get("scopes", []),
        }
    except Exception as e:
        logger.error("auth_decode_error", error=str(e))
        raise AuthenticationError("Invalid authentication token")


async def require_scope(
    scope: str,
    auth_context: Annotated[dict, Depends(get_auth_context)],
) -> dict:
    """Require a specific scope for the operation."""
    verify_scope(scope, auth_context["scopes"])
    return auth_context


def get_tenant_context(auth_context: Annotated[dict, Depends(get_auth_context)]) -> str:
    """Extract tenant ID from auth context."""
    return auth_context["tenant_id"]


def get_application_id(auth_context: Annotated[dict, Depends(get_auth_context)]) -> Optional[str]:
    """Extract application ID from auth context."""
    return auth_context.get("application_id")


async def get_context(
    request_id: Annotated[str, Depends(get_request_id)],
    tenant_id: Annotated[str, Depends(get_tenant_context)],
    application_id: Annotated[Optional[str], Depends(get_application_id)],
    auth_context: Annotated[dict, Depends(get_auth_context)],
) -> dict:
    """Get full request context."""
    return {
        "request_id": request_id,
        "tenant_id": tenant_id,
        "application_id": application_id,
        "subject": auth_context.get("subject"),
        "scopes": auth_context.get("scopes", []),
    }
