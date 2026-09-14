"""
SIMORGH Platform API - Core Exceptions
"""
from typing import Any, Optional


class PlatformException(Exception):
    """Base exception for all platform errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self, request_id: Optional[str] = None) -> dict[str, Any]:
        """Convert exception to standardized error response."""
        error_dict = {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }
        if request_id:
            error_dict["error"]["request_id"] = request_id
        if self.details:
            error_dict["error"]["details"] = self.details
        return error_dict


class AuthenticationError(PlatformException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
        )


class AuthorizationError(PlatformException):
    """Authorization failed - insufficient permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
        )


class TenantIsolationError(PlatformException):
    """Cross-tenant access attempt."""
    
    def __init__(self, message: str = "Cross-tenant access not allowed"):
        super().__init__(
            message=message,
            code="TENANT_ISOLATION_ERROR",
            status_code=403,
        )


class ProviderUnavailableError(PlatformException):
    """AI provider is unavailable."""
    
    def __init__(self, message: str = "AI provider is unavailable"):
        super().__init__(
            message=message,
            code="PROVIDER_UNAVAILABLE",
            status_code=503,
        )


class ProviderConfigurationError(PlatformException):
    """AI provider is not configured."""
    
    def __init__(self, message: str = "AI provider is not configured"):
        super().__init__(
            message=message,
            code="PROVIDER_NOT_CONFIGURED",
            status_code=500,
        )


class RateLimitError(PlatformException):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class ValidationError(PlatformException):
    """Request validation failed."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(PlatformException):
    """Resource not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
        )


class AIProviderError(PlatformException):
    """AI provider returned an error."""
    
    def __init__(self, message: str = "AI provider error", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="AI_PROVIDER_ERROR",
            status_code=502,
            details=details,
        )
