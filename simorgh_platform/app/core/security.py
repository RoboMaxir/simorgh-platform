"""
SIMORGH Platform API - Authentication and Authorization
"""
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError


settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def generate_api_key() -> str:
    """Generate a secure API key with prefix."""
    random_part = secrets.token_urlsafe(32)
    return f"{settings.api_key_prefix}{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return hash_api_key(plain_key) == hashed_key


def create_access_token(
    subject: str,
    tenant_id: str,
    application_id: str,
    scopes: list[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token with tenant and application context."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    to_encode = {
        "sub": subject,
        "tenant_id": tenant_id,
        "application_id": application_id,
        "scopes": scopes,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def verify_scope(required_scope: str, granted_scopes: list[str]) -> bool:
    """Verify if a required scope is in the granted scopes."""
    if not granted_scopes:
        return False
    
    # Check for exact match or wildcard
    return required_scope in granted_scopes or "*" in granted_scopes


def require_scope(required_scope: str, granted_scopes: list[str]) -> None:
    """Require a specific scope, raise AuthorizationError if not present."""
    if not verify_scope(required_scope, granted_scopes):
        raise AuthorizationError(f"Missing required scope: {required_scope}")
