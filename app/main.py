"""
SIMORGH Platform API - Main Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.errors import platform_exception_handler, generic_exception_handler, PlatformError
from app.api.v1 import v1_router
from app.api.v1.health import router as health_router
from app.core.exceptions import PlatformException
from app.api.v1.dependencies import get_request_id

settings = get_settings()

# Configure structured logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

logger = logging.getLogger("simorgh")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    if settings.is_production and settings.jwt_secret_key.startswith("change-this"):
        raise RuntimeError("JWT_SECRET_KEY must be set to a non-default value in production")
    logger.info("simorgh_platform_starting version=%s", settings.app_version)
    yield
    logger.info("simorgh_platform_stopping")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="SIMORGH Platform API - Shared infrastructure layer for SIMORGH ecosystem",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware (configure appropriately for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(PlatformError, platform_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.exception_handler(PlatformException)
async def platform_exception(request: Request, exc: PlatformException):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict(getattr(request.state, "request_id", None)))

# Include routers
app.include_router(v1_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    import uuid
    request.state.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response
