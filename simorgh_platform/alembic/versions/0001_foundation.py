"""Create the complete SIMORGH platform foundation schema.

Revision ID: 0001_foundation
Revises: None
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = '0001_foundation'
down_revision = None
branch_labels = None
depends_on = None
UUID = postgresql.UUID(as_uuid=True)
TS = sa.DateTime(timezone=True)

def id_col(): return sa.Column('id', UUID, primary_key=True)
def timestamps(): return [sa.Column('created_at', TS, nullable=False), sa.Column('updated_at', TS, nullable=False)]
def upgrade():
    op.create_table('tenants', id_col(), sa.Column('name',sa.String(255),nullable=False),sa.Column('slug',sa.String(100),nullable=False),sa.Column('is_active',sa.Boolean(),nullable=False),*timestamps(),sa.UniqueConstraint('slug'))
    op.create_index('ix_tenants_slug','tenants',['slug'])
    op.create_table('applications',id_col(),sa.Column('name',sa.String(100),nullable=False),sa.Column('slug',sa.String(50),nullable=False),sa.Column('description',sa.Text()),sa.Column('is_active',sa.Boolean(),nullable=False),*timestamps(),sa.UniqueConstraint('slug'))
    op.create_index('ix_applications_slug','applications',['slug'])
    op.create_table('application_installations',id_col(),sa.Column('tenant_id',UUID,sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),sa.Column('application_id',UUID,sa.ForeignKey('applications.id',ondelete='CASCADE'),nullable=False),sa.Column('is_active',sa.Boolean(),nullable=False),*timestamps(),sa.UniqueConstraint('tenant_id','application_id',name='ix_unique_tenant_app'))
    op.create_index('ix_application_installations_tenant_id','application_installations',['tenant_id']);op.create_index('ix_application_installations_application_id','application_installations',['application_id'])
    op.create_table('credentials',id_col(),sa.Column('installation_id',UUID,sa.ForeignKey('application_installations.id',ondelete='CASCADE'),nullable=False),sa.Column('key_id',sa.String(64),nullable=False),sa.Column('secret_hash',sa.String(255),nullable=False),sa.Column('name',sa.String(100),nullable=False),sa.Column('scopes',sa.Text()),sa.Column('is_active',sa.Boolean(),nullable=False),sa.Column('expires_at',TS),sa.Column('last_used_at',TS),*timestamps())
    op.create_index('ix_credentials_key_id','credentials',['key_id']);op.create_index('ix_credentials_installation_id','credentials',['installation_id'])
    op.create_table('ai_usage',id_col(),sa.Column('tenant_id',sa.String(36),nullable=False),sa.Column('application_id',UUID,sa.ForeignKey('applications.id',ondelete='SET NULL')),sa.Column('installation_id',UUID,sa.ForeignKey('application_installations.id',ondelete='SET NULL')),sa.Column('request_id',sa.String(64),nullable=False),sa.Column('provider',sa.String(50),nullable=False),sa.Column('model',sa.String(100),nullable=False),sa.Column('logical_model',sa.String(100),nullable=False),sa.Column('operation',sa.String(50),nullable=False),sa.Column('input_tokens',sa.Integer()),sa.Column('output_tokens',sa.Integer()),sa.Column('total_tokens',sa.Integer()),sa.Column('latency_ms',sa.Integer()),sa.Column('status',sa.String(20),nullable=False),sa.Column('error_message',sa.Text()),sa.Column('estimated_cost',sa.Float()),sa.Column('metadata',sa.Text()),*timestamps())
    for name,col in [('ix_ai_usage_tenant_id','tenant_id'),('ix_ai_usage_application_id','application_id'),('ix_ai_usage_request_id','request_id')]: op.create_index(name,'ai_usage',[col])
    op.create_table('audit_events',id_col(),sa.Column('tenant_id',UUID,nullable=False),sa.Column('application_id',UUID,nullable=False),sa.Column('installation_id',UUID,nullable=False),sa.Column('credential_id',UUID),sa.Column('request_id',sa.String(64),nullable=False),sa.Column('actor_type',sa.String(20),nullable=False),sa.Column('actor_id',sa.String(255)),sa.Column('action',sa.String(100),nullable=False),sa.Column('resource_type',sa.String(100)),sa.Column('resource_id',sa.String(255)),sa.Column('metadata',postgresql.JSONB()),*timestamps())
    for name,cols in [('ix_audit_events_tenant_id',['tenant_id']),('ix_audit_events_application_id',['application_id']),('ix_audit_events_installation_id',['installation_id']),('ix_audit_events_request_id',['request_id']),('ix_audit_events_action',['action']),('ix_audit_tenant_created',['tenant_id','created_at']),('ix_audit_resource',['resource_type','resource_id'])]: op.create_index(name,'audit_events',cols)
    op.create_table('knowledge_documents',id_col(),sa.Column('tenant_id',UUID,nullable=False),sa.Column('application_id',UUID),sa.Column('title',sa.String(500),nullable=False),sa.Column('content',sa.Text(),nullable=False),sa.Column('source',sa.String(255)),sa.Column('mime_type',sa.String(100)),sa.Column('is_indexed',sa.Boolean()),sa.Column('indexed_at',TS),sa.Column('metadata',postgresql.JSONB()),*timestamps())
    op.create_index('ix_knowledge_documents_tenant_id','knowledge_documents',['tenant_id']);op.create_index('ix_knowledge_documents_application_id','knowledge_documents',['application_id']);op.create_index('ix_knowledge_documents_is_indexed','knowledge_documents',['is_indexed']);op.create_index('ix_knowledge_tenant_source','knowledge_documents',['tenant_id','source'])
    op.create_table('knowledge_chunks',id_col(),sa.Column('document_id',UUID,sa.ForeignKey('knowledge_documents.id',ondelete='CASCADE'),nullable=False),sa.Column('tenant_id',UUID,nullable=False),sa.Column('chunk_index',sa.Integer(),nullable=False),sa.Column('content',sa.Text(),nullable=False),sa.Column('embedding',postgresql.JSONB()),*timestamps())
    for name,cols in [('ix_knowledge_chunks_document_id',['document_id']),('ix_knowledge_chunks_tenant_id',['tenant_id']),('ix_chunk_document',['document_id','chunk_index']),('ix_chunk_tenant',['tenant_id'])]: op.create_index(name,'knowledge_chunks',cols)
def downgrade():
    op.drop_table('knowledge_chunks');op.drop_table('knowledge_documents');op.drop_table('audit_events');op.drop_table('ai_usage');op.drop_table('credentials');op.drop_table('application_installations');op.drop_table('applications');op.drop_table('tenants')
