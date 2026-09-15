"""Foundation-only knowledge endpoints."""
from typing import Annotated
from fastapi import APIRouter, Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import require_scope
from app.core.context import RequestContext
from app.core.errors import NotFoundError, ErrorCode
from app.db.session import get_db
from app.models.knowledge_document import KnowledgeDocument
router=APIRouter()
@router.post('/index')
async def index_document(_: Annotated[RequestContext, Depends(require_scope('knowledge.write'))]):
    return {'data': {'message':'Knowledge indexing is not enabled in this MVP.'}}
@router.post('/search')
async def search_knowledge(_: Annotated[RequestContext, Depends(require_scope('knowledge.read'))]):
    return {'data': {'results': []}}
@router.get('/documents/{document_id}')
async def get_document(context: Annotated[RequestContext, Depends(require_scope('knowledge.read'))], document_id: str=Path(...), db: AsyncSession=Depends(get_db)):
    document=(await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id==document_id, KnowledgeDocument.tenant_id==context.tenant_id))).scalar_one_or_none()
    if not document: raise NotFoundError(ErrorCode.DOCUMENT_NOT_FOUND, 'Document not found')
    return {'data': {'id':str(document.id),'title':document.title,'content':document.content,'metadata':document.metadata,'request_id':context.request_id}}
