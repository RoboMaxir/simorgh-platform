"""Compatibility exports for the single canonical v1 auth dependency."""
from app.api.v1.dependencies import get_current_context, get_request_id, require_scope

__all__ = ["get_current_context", "get_request_id", "require_scope"]
