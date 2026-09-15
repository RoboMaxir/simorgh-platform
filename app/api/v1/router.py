"""
SIMORGH Platform API - V1 API Router

Main router for version 1 of the API.
"""
from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.audit import router as audit_router
from app.api.v1.health import router as health_router


api_v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_v1_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_v1_router.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge"])
api_v1_router.include_router(audit_router, prefix="/audit", tags=["Audit"])
api_v1_router.include_router(health_router, tags=["Health"])
