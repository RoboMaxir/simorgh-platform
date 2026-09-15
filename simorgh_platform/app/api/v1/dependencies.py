"""
SIMORGH Platform API - API Dependencies

Authentication, authorization, and request context dependencies.
"""
import uuid
from typing import Optional
from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.core.context import RequestContext
from app.core.errors import (
    AuthenticationError,
    AuthorizationError,
    ErrorCode,
)


async def get_request_id(x_request_id: Optional[str] = Header(None)) -> str:
    """Extract or generate request ID."""
    if x_request_id:
        # Validate format (basic check)
        if len(x_request_id) > 64:
            return str(uuid.uuid4())
        return x_request_id
    return str(uuid.uuid4())


async def get_current_context(
    request: Request,
    authorization: Optional[str] = Header(None),
    request_id: str = Depends(get_request_id),
) -> RequestContext:
    """
    Extract request context from Bearer token.
    
    Validates token and builds RequestContext with tenant, application, and scopes.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError(
            ErrorCode.AUTHENTICATION_REQUIRED,
            "Bearer token required.",
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    payload = decode_access_token(token)
    
    if not payload:
        raise AuthenticationError(
            ErrorCode.INVALID_TOKEN,
            "Invalid or expired token.",
        )
    
    # Build context from token payload
    context = RequestContext.from_token_payload(payload, request_id)
    
    # Store in request state for logging/error handling
    request.state.request_id = request_id
    request.state.tenant_id = context.tenant_id
    request.state.application_id = context.application_id
    
    return context


def require_scope(required_scope: str):
    """
    Dependency factory that requires a specific scope.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(ctx: RequestContext = Depends(require_scope("ai.chat"))):
            ...
    """
    async def scope_checker(context: RequestContext = Depends(get_current_context)):
        if not context.has_scope(required_scope):
            raise AuthorizationError(
                ErrorCode.INSUFFICIENT_SCOPE,
                f"Missing required scope: {required_scope}",
            )
        return context
    
    return scope_checker
