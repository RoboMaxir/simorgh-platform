"""
SIMORGH Platform API - Error Handling

Standardized error codes and exception handling.
"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()


# Error code taxonomy
class ErrorCode:
    # Authentication
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Authorization
    INSUFFICIENT_SCOPE = "INSUFFICIENT_SCOPE"
    
    # Tenant/Application
    TENANT_NOT_FOUND = "TENANT_NOT_FOUND"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    INSTALLATION_NOT_FOUND = "INSTALLATION_NOT_FOUND"
    CREDENTIAL_NOT_FOUND = "CREDENTIAL_NOT_FOUND"
    
    # AI Provider
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    INVALID_MODEL = "INVALID_MODEL"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Knowledge
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    KNOWLEDGE_ERROR = "KNOWLEDGE_ERROR"
    
    # General
    INVALID_REQUEST = "INVALID_REQUEST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"


class PlatformError(Exception):
    """Base platform exception."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(PlatformError):
    """Authentication-related errors."""
    
    def __init__(self, code: str, message: str, status_code: int = 401):
        super().__init__(code, message, status_code)


class AuthorizationError(PlatformError):
    """Authorization-related errors."""
    
    def __init__(self, code: str, message: str, status_code: int = 403):
        super().__init__(code, message, status_code)


class NotFoundError(PlatformError):
    """Resource not found errors."""
    
    def __init__(self, code: str, message: str, status_code: int = 404):
        super().__init__(code, message, status_code)


class ProviderError(PlatformError):
    """AI provider errors."""
    
    def __init__(self, code: str, message: str, status_code: int = 503):
        super().__init__(code, message, status_code)


async def platform_exception_handler(request: Request, exc: PlatformError) -> JSONResponse:
    """Handle platform exceptions with standardized response."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(
        "platform_error",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        "unexpected_error",
        error=str(exc),
        request_id=request_id,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        },
    )
