"""Authenticated AI gateway endpoints."""
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import require_scope
from app.core.context import RequestContext
from app.db.session import get_db
from app.schemas.ai import ChatRequest, ChatResponse, EmbeddingsRequest, EmbeddingsResponse, ModelsResponse, ProvidersResponse, UsageEntry, UsageResponse
from app.services.ai.gateway import AIGateway
from app.services.ai.registry import get_provider_registry
from app.services.ai.usage import UsageTracker
router = APIRouter()
def gateway(db): return AIGateway(db, get_provider_registry())
@router.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest, context: Annotated[RequestContext, Depends(require_scope('ai.chat'))], db: AsyncSession = Depends(get_db)):
    r = await gateway(db).chat(tenant_id=context.tenant_id, application_id=context.application_id, installation_id=context.installation_id, request_id=context.request_id, messages=[m.model_dump() for m in request.messages], model=request.model, temperature=request.temperature, max_tokens=request.max_tokens, top_p=request.top_p, metadata=request.metadata)
    return ChatResponse(id=r.request_id, model=r.model, provider=r.provider, content=r.content, input_tokens=r.input_tokens, output_tokens=r.output_tokens, total_tokens=r.total_tokens, latency_ms=r.latency_ms or 0, request_id=r.request_id)
@router.post('/embeddings', response_model=EmbeddingsResponse)
async def embeddings(request: EmbeddingsRequest, context: Annotated[RequestContext, Depends(require_scope('ai.embeddings'))], db: AsyncSession = Depends(get_db)):
    r = await gateway(db).embeddings(tenant_id=context.tenant_id, application_id=context.application_id, installation_id=context.installation_id, request_id=context.request_id, input_text=request.input, model=request.model, metadata=request.metadata)
    return EmbeddingsResponse(embeddings=r.embeddings, model=r.model, provider=r.provider, input_tokens=r.total_tokens, request_id=r.request_id)
@router.get('/models', response_model=ModelsResponse)
async def models(_: Annotated[RequestContext, Depends(require_scope('ai.models.read'))]):
    result=[]
    for provider in get_provider_registry().values():
        if await provider.is_available(): result.extend(await provider.list_models())
    return ModelsResponse(models=result)
@router.get('/providers', response_model=ProvidersResponse)
async def providers(_: Annotated[RequestContext, Depends(require_scope('ai.models.read'))]):
    result=[]
    for key, provider in get_provider_registry().items():
        available=await provider.is_available(); result.append({'id':key,'name':provider.provider_name,'is_configured':available,'is_available':available})
    return ProvidersResponse(providers=result)
@router.get('/usage', response_model=UsageResponse)
async def usage(context: Annotated[RequestContext, Depends(require_scope('ai.usage.read'))], db: AsyncSession = Depends(get_db)):
    entries=await UsageTracker(db).get_usage(context.tenant_id)
    return UsageResponse(entries=[UsageEntry(request_id=e.request_id,provider=e.provider,model=e.model,operation=e.operation,input_tokens=e.input_tokens,output_tokens=e.output_tokens,total_tokens=e.total_tokens,status=e.status,timestamp=e.created_at.isoformat()) for e in entries],total_requests=len(entries),total_tokens=sum(e.total_tokens for e in entries))
