"""
SIMORGH Platform API - AI Usage Tracking Service

Tracks and records AI usage for monitoring and billing.
"""
from datetime import datetime, timezone
from typing import Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ai_usage import AIUsage
from app.core.logging import get_logger


logger = get_logger(__name__)


class UsageTracker:
    """Tracks AI usage across providers."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def record_usage(
        self,
        tenant_id: str,
        application_id: Optional[str],
        installation_id: Optional[str],
        logical_model: str,
        request_id: str,
        provider: str,
        model: str,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        latency_ms: int,
        status: str,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AIUsage:
        """Record AI usage entry."""
        
        # Estimate cost (simplified - can be enhanced per provider)
        estimated_cost = self._estimate_cost(provider, model, total_tokens)
        
        usage = AIUsage(
            tenant_id=tenant_id,
            application_id=application_id,
            installation_id=installation_id,
            logical_model=logical_model,
            request_id=request_id,
            provider=provider,
            model=model,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            estimated_cost=estimated_cost,
            metadata=json.dumps(metadata) if metadata else None,
        )
        
        self.db.add(usage)
        await self.db.flush()
        
        logger.info(
            "ai_usage_recorded request_id=%s provider=%s model=%s tokens=%s cost=%s",
            request_id, provider, model, total_tokens, estimated_cost,
        )
        
        return usage
    
    def _estimate_cost(
        self,
        provider: str,
        model: str,
        total_tokens: int,
    ) -> float:
        """Estimate cost based on provider/model (simplified)."""
        # Simplified pricing - can be enhanced with actual provider pricing
        pricing = {
            "openai": {
                "gpt-4": 0.00003,
                "gpt-4-turbo": 0.00001,
                "gpt-3.5-turbo": 0.0000005,
                "default": 0.000002,
            },
            "anthropic": {
                "claude-3-opus": 0.000015,
                "claude-3-sonnet": 0.000003,
                "claude-3-haiku": 0.00000025,
                "default": 0.000003,
            },
            "qwen": {
                "default": 0.000001,
            },
        }
        
        provider_pricing = pricing.get(provider, {}).get("default", 0.000002)
        model_pricing = pricing.get(provider, {}).get(model, provider_pricing)
        
        return total_tokens * model_pricing
    
    async def get_usage(
        self,
        tenant_id: str,
        limit: int = 100,
    ) -> list[AIUsage]:
        """Get recent usage for a tenant."""
        result = await self.db.execute(
            select(AIUsage)
            .where(AIUsage.tenant_id == tenant_id)
            .order_by(AIUsage.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_usage_summary(
        self,
        tenant_id: str,
    ) -> dict:
        """Get usage summary for a tenant."""
        result = await self.db.execute(
            select(
                AIUsage.provider,
                AIUsage.model,
            )
            .where(AIUsage.tenant_id == tenant_id)
        )
        rows = result.all()
        
        total_requests = len(rows)
        total_tokens = sum(row.total_tokens for row in rows) if rows else 0
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
        }
