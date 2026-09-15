"""Central provider-agnostic AI gateway with durable usage accounting."""
from typing import Any, Optional
from app.providers.base import ChatMessage
from app.services.ai.router import ModelRouter
from app.services.ai.usage import UsageTracker
from app.core.exceptions import AIProviderError
class AIGateway:
    def __init__(self, db_session, providers):
        self.db=db_session; self.providers=providers; self.router=ModelRouter(providers); self.usage_tracker=UsageTracker(db_session)
    async def chat(self, *, tenant_id, application_id, installation_id, request_id, messages, model, temperature=0.7, max_tokens=2000, top_p=1.0, metadata=None):
        provider_id, actual_model=await self.router.resolve_model(model)
        try:
            r=await self.providers[provider_id].chat([ChatMessage(m['role'],m['content']) for m in messages], actual_model, temperature, max_tokens, top_p=top_p, request_id=request_id)
            r.request_id=request_id
            await self.usage_tracker.record_usage(tenant_id=tenant_id,application_id=application_id,installation_id=installation_id,request_id=request_id,logical_model=model,provider=provider_id,model=actual_model,operation=(metadata or {}).get('operation','chat'),input_tokens=r.input_tokens,output_tokens=r.output_tokens,total_tokens=r.total_tokens,latency_ms=r.latency_ms or 0,status='success',metadata=metadata)
            return r
        except Exception as exc:
            await self.usage_tracker.record_usage(tenant_id=tenant_id,application_id=application_id,installation_id=installation_id,request_id=request_id,logical_model=model,provider=provider_id,model=actual_model,operation=(metadata or {}).get('operation','chat'),input_tokens=0,output_tokens=0,total_tokens=0,latency_ms=0,status='error',error_message=str(exc))
            raise AIProviderError('AI provider request failed') from exc
    async def embeddings(self, *, tenant_id, application_id, installation_id, request_id, input_text, model, metadata=None):
        provider_id, actual_model=await self.router.resolve_model(model)
        try:
            r=await self.providers[provider_id].embeddings(input_text, actual_model, request_id=request_id); r.request_id=request_id
            await self.usage_tracker.record_usage(tenant_id=tenant_id,application_id=application_id,installation_id=installation_id,request_id=request_id,logical_model=model,provider=provider_id,model=actual_model,operation='embeddings',input_tokens=r.total_tokens,output_tokens=0,total_tokens=r.total_tokens,latency_ms=r.latency_ms or 0,status='success',metadata=metadata)
            return r
        except Exception as exc:
            await self.usage_tracker.record_usage(tenant_id=tenant_id,application_id=application_id,installation_id=installation_id,request_id=request_id,logical_model=model,provider=provider_id,model=actual_model,operation='embeddings',input_tokens=0,output_tokens=0,total_tokens=0,latency_ms=0,status='error',error_message=str(exc))
            raise AIProviderError('AI provider request failed') from exc
