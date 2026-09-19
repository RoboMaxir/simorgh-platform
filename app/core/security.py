"""
SIMORGH Platform API - Security Utilities

Handles password hashing, JWT token creation/validation.
"""
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

from app.config import get_settings

settings = get_settings()

# Argon2 hasher with configured parameters
password_hasher = PasswordHasher(
    memory_cost=settings.argon2_memory_cost,
    time_cost=settings.argon2_time_cost,
    parallelism=settings.argon2_parallelism,
)


def hash_secret(secret: str) -> str:
    """Hash a secret using Argon2."""
    return password_hasher.hash(secret)


def verify_secret(secret: str, secret_hash: str) -> bool:
    """Verify a secret against its hash."""
    try:
        password_hasher.verify(secret_hash, secret)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        password_hasher.verify(password_hash, password)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_scope(required_scope: str, scopes: List[str]) -> bool:
    """Verify if required scope is present in the list of scopes."""
    if not scopes:
        return False
    return required_scope in scopes or "*" in scopes
