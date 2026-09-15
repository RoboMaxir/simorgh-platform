"""
SIMORGH Platform API - Health Endpoints

Provides liveness and readiness checks.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, engine

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Liveness check - verifies the process is alive.
    
    Does NOT check database or external dependencies.
    """
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check - verifies platform runtime and database are ready.
    
    Does NOT fail if external AI providers are unavailable.
    """
    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}
