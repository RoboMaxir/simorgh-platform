"""
SIMORGH Platform API - Structured Logging
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.config import get_settings


settings = get_settings()


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Shared processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if settings.log_format == "json":
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        shared_processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
