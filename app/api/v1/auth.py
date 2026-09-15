"""
SIMORGH Platform API - Authentication Endpoints

Handles credential-based token exchange.
"""
import base64
import json
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.credential import Credential
from app.models.application_installation import ApplicationInstallation
from app.core.security import verify_secret, create_access_token
from app.core.errors import AuthenticationError, ErrorCode
from app.config import get_settings

router = APIRouter()


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


@router.post("/token")
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
    try:
        scopes = json.loads(credential.scopes or "[]")
    except (json.JSONDecodeError, TypeError) as exc:
        raise AuthenticationError(ErrorCode.INVALID_CREDENTIALS, "Credential scope configuration is invalid.") from exc
    if not isinstance(scopes, list) or not all(isinstance(scope, str) and scope for scope in scopes):
        raise AuthenticationError(ErrorCode.INVALID_CREDENTIALS, "Credential scope configuration is invalid.")
    token_data = {
        "tenant_id": str(installation.tenant_id),
        "application_id": str(installation.application_id),
        "installation_id": str(installation.id),
        "credential_id": str(credential.id),
        "scopes": scopes,
    }
    
    # Create access token
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=get_settings().access_token_expire_minutes),
    )
    
    return {
        "data": {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": get_settings().access_token_expire_minutes * 60,
            "scope": token_data["scopes"],
        }
    }
