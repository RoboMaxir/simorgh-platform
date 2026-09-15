"""Tenant-isolated append-only audit API."""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import require_scope
from app.core.context import RequestContext
from app.db.session import get_db
from app.models.audit_event import AuditEvent
router=APIRouter()
@router.post('/events')
async def record_audit_event(event_data: dict, context: Annotated[RequestContext, Depends(require_scope('audit.write'))], db: AsyncSession=Depends(get_db)):
    action=event_data.get('action')
    if not isinstance(action,str) or not action: return {'error': {'code':'INVALID_REQUEST','message':'action is required','request_id':context.request_id}}
    event=AuditEvent(tenant_id=context.tenant_id,application_id=context.application_id,installation_id=context.installation_id,credential_id=context.credential_id,request_id=context.request_id,actor_type='service',actor_id=context.application_id,action=action,resource_type=event_data.get('resource_type'),resource_id=event_data.get('resource_id'),metadata=event_data.get('metadata'))
    db.add(event); await db.flush()
    return {'data': {'id':str(event.id),'request_id':context.request_id}}
@router.get('/events')
async def list_audit_events(context: Annotated[RequestContext, Depends(require_scope('audit.read'))], db: AsyncSession=Depends(get_db), page:int=Query(1,ge=1), page_size:int=Query(20,ge=1,le=100)):
    query=select(AuditEvent).where(AuditEvent.tenant_id==context.tenant_id).order_by(AuditEvent.created_at.desc())
    total=(await db.execute(select(func.count()).select_from(AuditEvent).where(AuditEvent.tenant_id==context.tenant_id))).scalar_one()
    rows=(await db.execute(query.offset((page-1)*page_size).limit(page_size))).scalars().all()
    return {'data': {'events':[{'id':str(e.id),'action':e.action,'resource_type':e.resource_type,'resource_id':e.resource_id,'created_at':e.created_at.isoformat()} for e in rows], 'total':total,'page':page,'page_size':page_size,'request_id':context.request_id}}
