# SIMORGH PLATFORM — ARCHITECTURE BASELINE

## 1. System Architecture

**Pattern:** Modular Monolith  
**Language:** Python 3.11+  
**Framework:** FastAPI  
**Database:** PostgreSQL 15+  
**ORM:** SQLAlchemy 2.0 (async)  
**Migrations:** Alembic  

### Logical Layers

```text
┌─────────────────────────────────────────┐
│           API Layer (FastAPI)           │
│  /api/v1/* endpoints, request/response  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Service Layer (Business)        │
│   Use cases, orchestration, validation  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│       Domain / Contracts Layer          │
│    Interfaces, entities, value objects  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Infrastructure / Providers         │
│  DB, AI providers, external integrations│
└─────────────────────────────────────────┘
```

### Module Structure

```text
simorgh_platform/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── api/
│   │   └── v1/                 # API version 1 endpoints
│   │       ├── health.py       # Health check endpoints
│   │       ├── ai.py           # AI gateway endpoints
│   │       ├── knowledge.py    # Knowledge endpoints
│   │       └── audit.py        # Audit endpoints
│   ├── core/
│   │   ├── security.py         # Authentication, authorization
│   │   ├── context.py          # Request context management
│   │   ├── errors.py           # Error handling, standard responses
│   │   └── logging.py          # Structured logging
│   ├── db/
│   │   ├── session.py          # Database session management
│   │   └── base.py             # Base model class
│   ├── models/
│   │   ├── tenant.py           # Tenant model
│   │   ├── application.py      # Application model
│   │   ├── credential.py       # Credential model
│   │   ├── ai_usage.py         # AI usage tracking
│   │   └── audit_event.py      # Audit event model
│   ├── schemas/
│   │   ├── ai.py               # AI request/response schemas
│   │   ├── knowledge.py        # Knowledge schemas
│   │   └── audit.py            # Audit schemas
│   ├── services/
│   │   ├── ai_gateway.py       # AI routing, provider selection
│   │   ├── knowledge.py        # Knowledge retrieval service
│   │   └── audit.py            # Audit logging service
│   └── providers/
│       ├── base.py             # Base AI provider interface
│       ├── openai.py           # OpenAI adapter
│       └── anthropic.py        # Anthropic adapter (future)
├── migrations/                  # Alembic migrations
├── tests/                       # Test suite
├── pyproject.toml              # Dependencies
├── .env.example                # Environment template
├── README.md                   # Documentation
└── API_CONTRACT.md             # API specification
```

---

## 2. Core Modules

| Module | Responsibility | MVP Status |
|--------|----------------|------------|
| **Identity** | Tenant, Application, Credential management | ✅ MVP |
| **Auth** | Authentication, Authorization, Scopes | ✅ MVP |
| **AI Gateway** | Provider abstraction, routing, usage tracking | ✅ MVP |
| **Knowledge** | Search, retrieve, index abstraction | 🟡 Foundation |
| **Audit** | Event logging, traceability | ✅ MVP |
| **Health** | Liveness, readiness checks | ✅ MVP |
| **Events** | Platform events (in-process) | ⏸️ Deferred |
| **Notifications** | Notification delivery | ⏸️ Deferred |
| **Files** | File storage abstraction | ⏸️ Deferred |
| **Memory** | Persistent entity memory | ⏸️ Deferred |

---

## 3. MVP Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Process alive check |
| GET | `/ready` | Dependencies ready check |

### Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/token` | Exchange credentials for token | Basic |

### AI Gateway

| Method | Path | Description | Scope |
|--------|------|-------------|-------|
| POST | `/api/v1/ai/chat` | Provider-agnostic chat completion | `ai.chat` |
| POST | `/api/v1/ai/embeddings` | Generate embeddings | `ai.embeddings` |
| GET | `/api/v1/ai/models` | List available logical models | `ai.models.read` |
| GET | `/api/v1/ai/providers` | List configured providers | `ai.models.read` |
| GET | `/api/v1/ai/usage` | Get usage statistics | `ai.usage.read` |

### Knowledge (Foundation)

| Method | Path | Description | Scope |
|--------|------|-------------|-------|
| POST | `/api/v1/knowledge/search` | Search knowledge base | `knowledge.search` |
| POST | `/api/v1/knowledge/retrieve` | Retrieve specific document | `knowledge.retrieve` |
| POST | `/api/v1/knowledge/index` | Index new document | `knowledge.write` |

### Audit

| Method | Path | Description | Scope |
|--------|------|-------------|-------|
| POST | `/api/v1/audit/events` | Record audit event | `audit.write` |
| GET | `/api/v1/audit/events` | Query audit events | `audit.read` |

---

## 4. Database Design

### Entity Relationship Diagram

```text
┌─────────────────┐       ┌─────────────────┐
│     tenants     │       │   applications  │
├─────────────────┤       ├─────────────────┤
│ id (UUID)       │◄──────│ id (UUID)       │
│ name            │       │ tenant_id (FK)  │
│ slug            │       │ name            │
│ status          │       │ slug            │
│ created_at      │       │ status          │
│ updated_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   credentials   │
                          ├─────────────────┤
                          │ id (UUID)       │
                          │ application_id  │
                          │ key_id          │
                          │ secret_hash     │
                          │ scopes (JSON)   │
                          │ status          │
                          │ expires_at      │
                          │ created_at      │
                          │ last_used_at    │
                          └─────────────────┘

┌─────────────────────────────────────────┐
│              ai_usage                   │
├─────────────────────────────────────────┤
│ id (UUID)                               │
│ tenant_id (FK)                          │
│ application_id (FK)                     │
│ request_id (UUID)                       │
│ provider                                │
│ model                                   │
│ operation                               │
│ input_tokens                            │
│ output_tokens                           │
│ total_tokens                            │
│ latency_ms                              │
│ status                                  │
│ estimated_cost                          │
│ created_at                              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│            audit_events                 │
├─────────────────────────────────────────┤
│ id (UUID)                               │
│ tenant_id (FK)                          │
│ application_id (FK)                     │
│ actor_id                                │
│ action                                  │
│ resource                                │
│ resource_id                             │
│ request_id (UUID)                       │
│ metadata (JSON)                         │
│ created_at                              │
└─────────────────────────────────────────┘
```

### Identifier Strategy

**Decision:** UUIDv7  
**Rationale:** 
- Time-sortable for better database performance
- Distributed system friendly
- No coordination required
- PostgreSQL indexes efficiently on UUID

### Timestamp Strategy

- All timestamps stored as `TIMESTAMPTZ` (UTC)
- Exposed as ISO 8601 strings in API responses
- Python: `datetime.now(timezone.utc)`

---

## 5. Authentication Model

### Credential-Based Authentication

```text
Application
    │
    ├──► Requests credential from Platform Admin
    │
    ├──► Receives:
    │     - key_id (public identifier)
    │     - secret (shown once, never stored by platform)
    │
    └──► Uses HTTP Basic Auth:
          Authorization: Basic base64(key_id:secret)
```

### Token Flow (Optional for future)

```text
Credential ──► /auth/token ──► JWT Access Token
                    │
                    └──► Valid for N minutes
                         Scoped to credential permissions
```

### Security Properties

- Secrets hashed using `argon2` or `bcrypt`
- Secrets shown only at creation time
- Credentials can be rotated/revoked
- Rate limiting per credential

---

## 6. Authorization Model

### Scope-Based Access Control

Initial scopes:

```text
ai.chat              - Chat completion
ai.embeddings        - Embedding generation
ai.models.read       - List models/providers
ai.usage.read        - Read usage statistics

knowledge.search     - Search knowledge base
knowledge.retrieve   - Retrieve documents
knowledge.write      - Index documents

audit.write          - Record audit events
audit.read           - Query audit events
```

### Scope Assignment

```python
credential.scopes = ["ai.chat", "ai.embeddings"]
```

### Enforcement

```python
@require_scope("ai.chat")
async def chat_endpoint(...):
    ...
```

---

## 7. AI Provider Architecture

### Provider Interface

```python
class AIProvider(ABC):
    
    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> ChatResponse:
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        texts: list[str],
        model: str,
        **kwargs
    ) -> EmbeddingsResponse:
        pass
    
    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        pass
```

### Provider Adapters

| Provider | Status | Notes |
|----------|--------|-------|
| OpenAI | ✅ MVP | Primary provider |
| OpenAI-Compatible | ✅ MVP | Local LLMs, Qwen |
| Anthropic | ⏸️ Deferred | Future |
| Qwen Native | ⏸️ Deferred | Via compatible adapter |

---

## 8. Model Registry

### Logical vs Physical Models

```text
Logical Model (Application sees)
    │
    ├──► reasoning
    │     └──► Maps to: claude-sonnet-4, gpt-4, qwen-max
    │
    ├──► fast
    │     └──► Maps to: gpt-4o-mini, haiku
    │
    ├──► cheap
    │     └──► Maps to: lowest cost available
    │
    └──► embedding
          └──► Maps to: text-embedding-3-large
```

### Routing Configuration

```yaml
logical_models:
  reasoning:
    priority:
      - provider: anthropic
        model: claude-sonnet-4
      - provider: openai
        model: gpt-4
    fallback:
      provider: openai-compatible
      model: qwen-max
  
  fast:
    priority:
      - provider: openai
        model: gpt-4o-mini
      - provider: anthropic
        model: haiku
  
  embedding:
    priority:
      - provider: openai
        model: text-embedding-3-large
```

---

## 9. Routing Strategy

### Deterministic Routing Algorithm

```text
1. Check explicit model override in request
2. Resolve logical model to physical models
3. Filter by provider availability
4. Apply routing policy (cost/latency/privacy)
5. Select first available
6. On failure, try fallback
```

### Error Classification

| Error Type | Retry? | Fallback? |
|------------|--------|-----------|
| Timeout | Yes (bounded) | Yes |
| Rate Limit | Yes (with backoff) | Yes |
| Provider Unavailable | Yes | Yes |
| Invalid Request | No | No |
| Auth Failure | No | No |
| Malformed Response | Yes | Yes |

---

## 10. Usage Tracking

### Tracked Fields

```python
{
    "id": "uuid",
    "tenant_id": "uuid",
    "application_id": "uuid",
    "request_id": "uuid",
    "provider": "openai",
    "model": "gpt-4",
    "operation": "chat",
    "input_tokens": 150,
    "output_tokens": 300,
    "total_tokens": 450,
    "latency_ms": 1250,
    "status": "success",
    "estimated_cost": 0.012,
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Cost Calculation (Future)

- Store provider-specific pricing tables
- Calculate actual cost post-request
- Support budget alerts

---

## 11. Knowledge Architecture

### Abstraction Layers

```text
Application
    │
    ▼
Knowledge Service
    │
    ├──► Retrieval Engine (interface)
    │     ├── PostgreSQL + pgvector
    │     └── External vector DB (future)
    │
    └──► Storage Backend
          ├── PostgreSQL (documents)
          └── Object storage (files)
```

### MVP Implementation

- PostgreSQL with pgvector extension
- Hybrid search (keyword + vector)
- Simple document/chunk model

---

## 12. Audit Architecture

### Append-Only Events

```python
class AuditEvent(Base):
    id: UUID
    tenant_id: UUID
    application_id: UUID
    actor_id: str
    action: str  # CREATE, UPDATE, DELETE, ACCESS
    resource: str  # "product", "decision"
    resource_id: str
    request_id: UUID
    metadata: dict  # Additional context
    created_at: datetime
```

### Immutability

- No UPDATE operations allowed
- Soft delete not applicable
- Retention policy via TTL (future)

---

## 13. Security Model

### Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| Cross-tenant access | Tenant ID from auth context, not request body |
| Credential theft | Argon2 hashing, secure transmission |
| Scope escalation | Explicit scope checking on every endpoint |
| Secret exposure | Never log secrets, redact in errors |
| SSRF | Validate provider URLs, no arbitrary URL execution |
| Injection | Parameterized queries, input validation |
| Rate abuse | Per-credential rate limiting |

### Tenant Isolation Guarantee

```text
Query: SELECT * FROM X WHERE tenant_id = :context_tenant_id
                                         ↑
                            From authenticated context
                            NOT from request body
```

---

## 14. Dependency List

### Core Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = "^0.27.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
sqlalchemy = {version = "^2.0.0", extras = ["asyncio"]}
asyncpg = "^0.29.0"
alembic = "^1.13.0"
httpx = "^0.26.0"  # Async HTTP client for providers
python-jose = "^3.3.0"  # JWT handling
passlib = {version = "^1.7.0", extras = ["bcrypt"]}
argon2-cffi = "^23.1.0"
structlog = "^24.1.0"  # Structured logging
```

### Development Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
httpx = "^0.26.0"
pytest-cov = "^4.1.0"
black = "^24.1.0"
ruff = "^0.1.0"
mypy = "^1.8.0"
```

---

## 15. Deferred Features

| Feature | Reason | Future Consideration |
|---------|--------|---------------------|
| Microservices | Over-engineering for MVP | Extract if scale requires |
| Kafka/Redis | No distributed queue need yet | In-process events first |
| Vector DB cluster | pgvector sufficient for MVP | External if performance needs |
| Autonomous AI routing | Deterministic is safer initially | ML-based later |
| Enterprise IAM | Simple credential auth sufficient | OAuth2/OIDC when needed |
| Billing system | Usage tracking is foundation | Add billing layer later |
| Advanced Memory | Knowledge foundation first | Separate memory engine |
| Full Notification system | Internal events sufficient | SMS/Email providers later |
| Complex File storage | Abstract interface first | S3/GCS integration later |

---

## 16. Files to Create

### Phase 1: Foundation

```
simorgh_platform/
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
├── API_CONTRACT.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       └── router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── context.py
│   │   ├── errors.py
│   │   └── logging.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── base.py
│   └── models/
│       ├── __init__.py
│       ├── tenant.py
│       └── application.py
└── migrations/
    ├── env.py
    └── script.py.mako
```

### Phase 2: AI Gateway

```
app/
├── schemas/
│   └── ai.py
├── services/
│   └── ai_gateway.py
├── providers/
│   ├── __init__.py
│   ├── base.py
│   └── openai.py
└── api/v1/
    └── ai.py
```

### Phase 3: Complete MVP

```
app/
├── models/
│   ├── credential.py
│   ├── ai_usage.py
│   └── audit_event.py
├── schemas/
│   ├── auth.py
│   ├── knowledge.py
│   └── audit.py
├── services/
│   ├── auth.py
│   ├── knowledge.py
│   └── audit.py
├── providers/
│   └── openai_compatible.py
└── api/v1/
    ├── auth.py
    ├── knowledge.py
    └── audit.py
```

---

## 17. Implementation Order

```text
PHASE 1: Project Foundation
  ✓ Create project structure
  ✓ Configure dependencies
  ✓ Setup configuration management
  ✓ Implement structured logging
  ✓ Create database session management

PHASE 2: Database & Models
  ✓ Define base model class
  ✓ Create tenant model
  ✓ Create application model
  ✓ Create credential model
  ✓ Create initial migration

PHASE 3: Authentication
  ✓ Implement credential verification
  ✓ Create request context extraction
  ✓ Implement scope checking decorator
  ✓ Create auth middleware

PHASE 4: AI Gateway Foundation
  ✓ Define AI provider interface
  ✓ Implement OpenAI adapter
  ✓ Implement OpenAI-compatible adapter
  ✓ Create model routing logic

PHASE 5: AI API
  ✓ Define AI schemas
  ✓ Implement chat endpoint
  ✓ Implement embeddings endpoint
  ✓ Implement models/providers listing
  ✓ Add usage tracking

PHASE 6: Knowledge Foundation
  ✓ Define knowledge schemas
  ✓ Implement retrieval abstraction
  ✓ Create knowledge endpoints

PHASE 7: Audit & Health
  ✓ Define audit event model
  ✓ Implement audit service
  ✓ Create audit endpoints
  ✓ Implement health checks

PHASE 8: SDK
  ✓ Create basic Python SDK
  ✓ Implement AI client
  ✓ Implement auth handling

PHASE 9: Testing
  ✓ Unit tests for providers
  ✓ Integration tests for AI endpoints
  ✓ Security tests for tenant isolation
  ✓ API contract tests

PHASE 10: Documentation
  ✓ Update README
  ✓ Document API contracts
  ✓ Create deployment guide
```

---

## 18. Success Criteria

- [ ] Server starts successfully
- [ ] Database connection works
- [ ] Migrations apply cleanly
- [ ] `/health` returns 200
- [ ] `/ready` checks dependencies
- [ ] Authentication validates credentials
- [ ] Tenant isolation enforced
- [ ] AI chat endpoint works
- [ ] Provider abstraction functions
- [ ] Routing selects correct model
- [ ] Usage records created
- [ ] Standard error format used
- [ ] Request IDs propagate
- [ ] Audit events recorded
- [ ] Tests pass (>80% critical paths)
- [ ] OpenAPI documentation complete
- [ ] No secrets in codebase
- [ ] Council can integrate via SDK

---

## 19. Next Steps

1. **Create project files** - Establish the foundational structure
2. **Implement authentication** - Build the security boundary first
3. **Build AI gateway** - Core platform capability
4. **Add knowledge foundation** - Prepare for RAG features
5. **Integrate Council** - Validate with real consumer
6. **Iterate based on feedback** - Refine based on actual usage

---

*This architecture baseline serves as the implementation contract for the SIMORGH Platform API MVP.*
