"""
SIMORGH Platform API - Core Module

Core utilities, context, errors, and security.
"""
from .security import hash_secret, verify_secret, create_access_token, decode_access_token
from .context import RequestContext
from .errors import (
    ErrorCode,
    PlatformError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ProviderError,
    platform_exception_handler,
    generic_exception_handler,
)

__all__ = [
    "hash_secret",
    "verify_secret",
    "create_access_token",
    "decode_access_token",
    "RequestContext",
    "ErrorCode",
    "PlatformError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ProviderError",
    "platform_exception_handler",
    "generic_exception_handler",
]
