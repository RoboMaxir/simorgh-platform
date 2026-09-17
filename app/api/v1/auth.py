"""
SIMORGH Platform API - Authentication Endpoints

Handles credential-based token exchange and user authentication.
"""
import base64
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.models.credential import Credential
from app.models.application_installation import ApplicationInstallation
from app.models.user import User
from app.core.security import verify_secret, create_access_token, verify_password
from app.core.errors import AuthenticationError, ErrorCode

router = APIRouter()


class TokenRequest(BaseModel):
    """Request model for email/password login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for token endpoints."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: Optional[dict] = None


def parse_basic_auth(authorization: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Parse Basic Auth header to extract key_id and secret."""
    if not authorization or not authorization.startswith("Basic "):
        return None, None
    
    try:
        credentials = base64.b64decode(authorization[6:]).decode("utf-8")
        key_id, secret = credentials.split(":", 1)
        return key_id, secret
    except Exception:
        return None, None


@router.post("/login", response_model=TokenResponse)
async def login_with_email(
    request: TokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a human user with email and password.
    
    **Request:**
    - email: User's email address
    - password: User's password
    
    **Response:** Bearer token with user info
    """
    # Find user by email
    result = await db.execute(
        select(User)
        .where(User.email == request.email)
        .where(User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationError(
            ErrorCode.INVALID_CREDENTIALS,
            "Invalid email or password.",
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise AuthenticationError(
            ErrorCode.INVALID_CREDENTIALS,
            "Invalid email or password.",
        )
    
    # Update last login
    from datetime import datetime, timezone
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Build token payload
    token_data = {
        "user_id": str(user.id),
        "workspace_id": str(user.workspace_id),
        "email": user.email,
        "name": user.name,
        "is_superuser": user.is_superuser,
    }
    
    # Create access token (24 hours for human users)
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=24),
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=86400,  # 24 hours in seconds
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "workspace_id": str(user.workspace_id),
        }
    )


@router.post("/token", response_model=TokenResponse)
async def exchange_token(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange credentials for a short-lived access token.
    
    **Authentication:** Basic (key_id:secret)
    
    **Response:** Bearer token with scopes
    """
    key_id, secret = parse_basic_auth(authorization)
    
    if not key_id or not secret:
        raise AuthenticationError(
            ErrorCode.AUTHENTICATION_REQUIRED,
            "Valid Basic authentication required.",
        )
    
    # Find credential by key_id
    result = await db.execute(
        select(Credential)
        .where(Credential.key_id == key_id)
        .where(Credential.is_active == True)
    )
    credential = result.scalar_one_or_none()
    
    if not credential:
        raise AuthenticationError(
            ErrorCode.INVALID_CREDENTIALS,
            "Invalid credentials.",
        )
    
    # Verify secret
    if not verify_secret(secret, credential.secret_hash):
        raise AuthenticationError(
            ErrorCode.INVALID_CREDENTIALS,
            "Invalid credentials.",
        )
    
    # Check expiration
    if credential.is_expired():
        raise AuthenticationError(
            ErrorCode.TOKEN_EXPIRED,
            "Credential has expired.",
        )
    
    # Get installation info
    result = await db.execute(
        select(ApplicationInstallation)
        .where(ApplicationInstallation.id == credential.installation_id)
        .where(ApplicationInstallation.is_active == True)
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise AuthenticationError(
            ErrorCode.INSTALLATION_NOT_FOUND,
            "Installation not found or inactive.",
        )
    
    # Build token payload
    scopes_str = credential.scopes or "[]"
    token_data = {
        "tenant_id": str(installation.tenant_id),
        "application_id": str(installation.application_id),
        "installation_id": str(installation.id),
        "credential_id": str(credential.id),
        "scopes": scopes_str if isinstance(scopes_str, list) else ["*"],  # Simplified for MVP
    }
    
    # Create access token
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=60),
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=3600,  # 1 hour in seconds
    )
