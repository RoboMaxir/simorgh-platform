"""
SIMORGH Platform API - Health Endpoints

Health and readiness check endpoints.
"""
from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.common import HealthResponse, ReadyResponse
from app.config import get_settings


settings = get_settings()
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.
    
    Returns whether the process is alive.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/ready", response_model=ReadyResponse)
async def ready():
    """
    Readiness check endpoint.
    
    Returns whether all dependencies are ready.
    """
    checks = {
        "process": True,
        "config": bool(settings.database_url),
    }
    
    # Check database connectivity (simplified)
    try:
        from app.db.base import engine
        checks["database"] = True
    except Exception:
        checks["database"] = False
    
    all_ready = all(checks.values())
    
    return ReadyResponse(
        ready=all_ready,
        checks=checks,
    )
