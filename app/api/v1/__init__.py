"""
SIMORGH Platform API - V1 API Module
"""
from fastapi import APIRouter

from .health import router as health_router
from .auth import router as auth_router
from .ai import router as ai_router
from .knowledge import router as knowledge_router
from .audit import router as audit_router

# Create main v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
v1_router.include_router(health_router)  # Health endpoints at root
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(ai_router, prefix="/ai", tags=["AI"])
v1_router.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge"])
v1_router.include_router(audit_router, prefix="/audit", tags=["Audit"])

__all__ = ["v1_router"]
