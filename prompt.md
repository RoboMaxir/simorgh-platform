# SIMORGH PLATFORM API — MASTER IMPLEMENTATION PROMPT

## ROLE

You are a **Senior Backend Architect, Platform Engineer, AI Infrastructure Engineer, Security Engineer, and Production Software Engineer**.

You are responsible for implementing the **SIMORGH Platform API**, the shared infrastructure/API layer of the SIMORGH ecosystem.

You are NOT building a generic API server.

You are building a **reusable internal platform layer** that allows every SIMORGH application to consume shared capabilities through one standardized interface.

The platform must become the common infrastructure layer between:

```text
SIMORGH Applications
        ↓
SIMORGH SDK / Platform API
        ↓
SIMORGH Platform
        ↓
AI / Knowledge / Infrastructure Providers
```

The first real consumer is expected to be the **SIMORGH AI Management Council**, but the architecture must support future applications such as Product, Service & Order, Fleet, and other OrgOS applications.

---

# 1. FIRST RULE — DO NOT START CODING IMMEDIATELY

Before modifying or creating code:

1. Inspect the entire repository.
2. Understand the current architecture.
3. Identify:

   * existing backend
   * existing database
   * existing models
   * authentication
   * configuration
   * migrations
   * API structure
   * existing AI integrations
   * existing dependencies
   * existing tests
   * existing frontend assumptions
4. Determine what can be reused.
5. Determine what must be refactored.
6. Determine what must be created.
7. Detect architectural conflicts.
8. Detect security risks.
9. Detect unnecessary complexity.

Do NOT assume the repository is empty.

Do NOT rewrite working systems without a reason.

Do NOT introduce new infrastructure merely because it is technically possible.

---

# 2. MANDATORY INITIAL REPORT

Before implementation, produce a concise but technical report:

```text
SIMORGH PLATFORM REPOSITORY AUDIT

1. Current Architecture
2. Existing Components
3. Existing API Endpoints
4. Existing Database
5. Existing Authentication
6. Existing AI/LLM Integration
7. Existing Dependencies
8. Reusable Components
9. Problems / Risks
10. Missing Components
11. Recommended Architecture
12. Implementation Plan
13. Files That Will Be Created
14. Files That Will Be Modified
15. Files That Must NOT Be Modified
```

Then proceed with implementation.

Do not wait for human approval unless the repository contains a critical ambiguity that makes implementation unsafe.

---

# 3. PRODUCT DEFINITION

SIMORGH Platform API is the shared platform layer for the SIMORGH ecosystem.

Its primary responsibility is to expose **common platform capabilities**, not business-domain logic.

The fundamental rule is:

> Shared infrastructure belongs to SIMORGH Platform.
> Business logic belongs to the consuming application.

For example:

### Platform owns

* LLM provider management
* AI model abstraction
* AI routing
* AI usage tracking
* API credentials
* Knowledge retrieval infrastructure
* Memory infrastructure
* Authentication
* Tenant context
* Application identity
* Audit
* Notifications
* Files
* Events
* Platform health

### Applications own

* Product BOM
* Product pricing
* Orders
* Production workflow
* Fleet maintenance
* Council decision logic
* Council debate logic
* Domain-specific business rules

DO NOT move application business logic into the Platform.

---

# 4. TARGET ARCHITECTURE

Implement the following conceptual architecture:

```text
                        ┌─────────────────────────┐
                        │    SIMORGH PLATFORM     │
                        │          API            │
                        └────────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
        AI PLATFORM            KNOWLEDGE              PLATFORM
              │                      │                      │
       ┌──────┼──────┐         ┌─────┼─────┐        ┌──────┼──────┐
       │      │      │         │     │     │        │      │      │
     LLM    Router  Usage     RAG  Memory Search   Auth   Audit  Events
       │
 ┌─────┼─────────────┐
 │     │             │
OpenAI Anthropic    Qwen
                     │
                  Local LLM
```

Applications:

```text
Council
Product
Service
Fleet
Future Apps
       │
       ▼
SIMORGH SDK
       │
       ▼
SIMORGH PLATFORM API
```

---

# 5. TECHNOLOGY

Prefer:

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* PostgreSQL
* pytest

Use asynchronous architecture where it provides real value.

Do NOT introduce:

* Kubernetes
* microservices
* Kafka
* Redis
* Celery
* vector databases
* complex service meshes

unless the repository or actual requirements clearly justify them.

The initial system should be a **modular monolith**.

Architecture must allow future extraction into services without requiring the entire application to be rewritten.

---

# 6. CORE DESIGN PRINCIPLE

The platform must have clear boundaries:

```text
API Layer
    ↓
Application / Use Case Layer
    ↓
Domain / Service Layer
    ↓
Infrastructure / Provider Layer
```

Do not put business logic inside FastAPI route functions.

Do not put database logic directly into route handlers.

Do not couple application code directly to OpenAI/Anthropic/Qwen SDKs.

---

# 7. AI PLATFORM

Build an AI Gateway.

Applications must NOT directly integrate with LLM providers.

Instead:

```text
Application
    ↓
SIMORGH AI API
    ↓
AI Gateway
    ↓
Model Router
    ↓
Provider Adapter
    ↓
LLM Provider
```

---

# 8. PROVIDER ABSTRACTION

Create a provider abstraction.

Conceptually:

```python
class AIProvider:
    async def chat(...)
    async def embeddings(...)
    async def list_models(...)
```

Implement provider adapters independently.

Initial providers should support architecture for:

* OpenAI
* Anthropic
* Qwen-compatible APIs
* Local/OpenAI-compatible endpoints

Do not hard-code providers throughout the codebase.

Provider-specific code must remain isolated.

Example:

```text
providers/
    base.py
    openai.py
    anthropic.py
    qwen.py
    openai_compatible.py
```

If a provider cannot support a requested capability, return a standardized platform error.

---

# 9. AI API

Implement versioned endpoints.

Base:

```text
/api/v1/
```

AI:

```text
POST /api/v1/ai/chat
POST /api/v1/ai/embeddings
GET  /api/v1/ai/models
GET  /api/v1/ai/providers
GET  /api/v1/ai/usage
```

The exact endpoint structure may be adjusted after repository inspection, but maintain semantic consistency.

---

# 10. AI REQUEST CONTRACT

Applications should not need provider-specific parameters.

Example:

```json
{
  "model": "reasoning",
  "messages": [
    {
      "role": "user",
      "content": "Analyze this decision."
    }
  ],
  "temperature": 0.2,
  "max_tokens": 2000,
  "metadata": {
    "app": "council",
    "operation": "decision_analysis"
  }
}
```

The platform may internally resolve:

```text
reasoning
    ↓
Routing Policy
    ↓
Claude / OpenAI / Qwen / Local
```

The application should not need to know the provider.

---

# 11. MODEL ROUTING

Implement a clean routing abstraction.

Routing should eventually support policies such as:

```text
reasoning
fast
cheap
private
local
embedding
vision
coding
```

Example:

```text
task = reasoning
privacy = high
budget = low

→ choose appropriate available model
```

However:

DO NOT build a complicated autonomous routing AI.

Initial routing should be deterministic and configurable.

Possible priority:

```text
Explicit model
    ↓
Routing policy
    ↓
Provider availability
    ↓
Fallback
```

---

# 12. PROVIDER CONFIGURATION

Never expose provider API keys through application code.

Store provider credentials securely through environment variables or a secure credential mechanism appropriate to the repository.

Applications should never contain:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
QWEN_API_KEY
```

The Platform owns provider credentials.

---

# 13. AI USAGE

Every AI request should be traceable.

Track at minimum:

```text
tenant
application
request_id
provider
model
operation
input tokens
output tokens
total tokens
latency
status
error
timestamp
estimated cost
```

Do not require perfect billing accuracy in MVP.

The architecture must allow accurate provider-specific cost calculation later.

---

# 14. REQUEST ID / TRACEABILITY

Every Platform API request must receive or generate:

```text
request_id
```

The ID must propagate through:

```text
Application
 ↓
Platform API
 ↓
AI Gateway
 ↓
Provider
```

Logs must make requests traceable.

---

# 15. TENANT CONTEXT

The platform must be multi-tenant ready.

Every relevant operation must have tenant context.

Never trust tenant IDs supplied only in request bodies.

Tenant context must originate from authenticated application/user context.

Conceptually:

```text
Authentication
      ↓
Tenant Context
      ↓
Authorization
      ↓
Operation
```

All tenant-owned database records must be designed with tenant isolation in mind.

PostgreSQL Row Level Security compatibility should be considered, but DO NOT implement RLS unless justified by the existing architecture.

---

# 16. APPLICATION IDENTITY

Applications must have their own identity.

Example:

```text
council
product
service
fleet
```

Platform requests should be attributable to an application.

Conceptually:

```text
Tenant
Application
User / Service Identity
Request
```

The platform must know:

```text
WHO
FROM WHICH APP
FOR WHICH TENANT
DID WHAT
```

---

# 17. AUTHENTICATION

Implement secure service-to-platform authentication.

Do not use hard-coded shared passwords.

Prefer:

```text
Application Credential / API Key
+
Tenant Context
+
Permission Scope
```

Design authentication so that it can later support:

* application credentials
* user tokens
* service accounts
* OAuth2/JWT if required

Do not overbuild OAuth infrastructure for MVP if it is not already present.

---

# 18. AUTHORIZATION

Introduce permission scopes.

Example:

```text
ai.chat
ai.embeddings
ai.models.read
knowledge.search
knowledge.write
audit.write
files.read
files.write
```

An application should receive only the capabilities it needs.

Council should not automatically receive every Platform capability.

---

# 19. KNOWLEDGE API

Create the foundation for a shared Knowledge service.

Initial API:

```text
POST /api/v1/knowledge/search
POST /api/v1/knowledge/retrieve
POST /api/v1/knowledge/index
```

The architecture should distinguish:

```text
Knowledge
Retrieval
Memory
Documents
Embeddings
```

Do NOT incorrectly treat RAG as memory.

---

# 20. KNOWLEDGE ABSTRACTION

Applications should request knowledge through a standard contract.

Example:

```json
{
  "query": "What are the previous decisions about this investment?",
  "top_k": 5,
  "filters": {
    "tenant_id": "...",
    "source": "council"
  }
}
```

The application must not care whether retrieval uses:

* PostgreSQL
* pgvector
* another vector store
* hybrid search
* future retrieval engine

Keep the storage/retrieval implementation behind an abstraction.

---

# 21. MEMORY

Treat Memory as a separate capability.

Conceptually:

```text
Knowledge
    =
stored organizational information

Memory
    =
persistent contextual information about entities,
interactions, decisions, preferences, and state
```

Do not implement a sophisticated memory engine unless required for the MVP.

Create clean interfaces so it can evolve.

---

# 22. AUDIT

Create a platform audit mechanism.

Example:

```text
POST /api/v1/audit/events
```

Record:

```text
tenant
application
actor
action
resource
resource_id
request_id
timestamp
metadata
```

Audit logs should be append-oriented.

Do not allow ordinary application code to silently modify historical audit records.

---

# 23. EVENTS

Create an event abstraction.

Example:

```text
event_name
tenant_id
application_id
actor_id
payload
timestamp
request_id
```

Initial implementation can be database-backed or in-process.

Do not introduce Kafka merely for architecture aesthetics.

---

# 24. NOTIFICATIONS

Prepare a notification abstraction:

```text
POST /api/v1/notifications
```

Initial implementation may only support internal/platform notifications.

Do not build a complete SMS/email provider ecosystem unless the repository already requires it.

---

# 25. FILES

Prepare a file abstraction.

Applications should eventually be able to use:

```text
POST /api/v1/files
GET  /api/v1/files/{id}
DELETE /api/v1/files/{id}
```

Storage must be abstracted.

Do not hard-code local filesystem assumptions into business logic.

---

# 26. HEALTH

Implement:

```text
GET /health
GET /ready
```

Health should distinguish:

```text
process alive
dependencies ready
```

Do not expose secrets or sensitive configuration.

---

# 27. CONFIGURATION

Use environment-based configuration.

Create/update:

```text
.env.example
```

Never commit real secrets.

Configuration should include provider configuration, database configuration, authentication configuration, and environment mode.

---

# 28. DATABASE

Use migrations.

Never rely on:

```text
create_all()
```

as the production migration strategy.

Use Alembic or the existing migration system.

Database models must be explicit.

Every model must have:

* primary key
* timestamps where appropriate
* tenant ownership where appropriate
* indexes where justified
* constraints where appropriate

Avoid excessive indexes.

---

# 29. API VERSIONING

All public Platform contracts should be versioned:

```text
/api/v1/
```

Do not create unstable unversioned endpoints that applications depend upon.

---

# 30. STANDARD ERROR FORMAT

All APIs must return a consistent error structure.

Conceptually:

```json
{
  "error": {
    "code": "PROVIDER_UNAVAILABLE",
    "message": "No AI provider is currently available.",
    "request_id": "..."
  }
}
```

Never expose:

* API keys
* stack traces
* internal file paths
* database credentials
* provider secrets

in production responses.

---

# 31. OBSERVABILITY

Implement structured logging.

Every important operation should include:

```text
request_id
tenant_id
application_id
operation
status
latency
```

AI requests should additionally include:

```text
provider
model
token usage
```

Do not log raw secrets.

Be careful with sensitive user/business content.

---

# 32. SECURITY REQUIREMENTS

Treat security as a first-class requirement.

At minimum:

* secret isolation
* authentication
* authorization
* tenant isolation
* input validation
* rate limiting architecture
* request tracing
* safe error handling
* auditability
* SSRF considerations for external provider URLs
* timeout handling
* provider failure isolation

Never blindly execute URLs supplied by clients.

Never trust tenant IDs from arbitrary payloads.

---

# 33. RESILIENCE

AI providers fail.

The Platform must handle:

```text
timeout
rate limit
provider unavailable
invalid response
authentication failure
malformed response
network failure
```

Implement appropriate:

```text
timeouts
controlled retries
fallbacks where configured
standardized errors
```

Do not retry non-idempotent operations blindly.

Do not create infinite retry loops.

---

# 34. RATE LIMITING

Design for rate limiting.

At minimum the architecture should allow limits by:

```text
tenant
application
provider
model
endpoint
```

A simple implementation is acceptable for MVP.

Do not introduce distributed infrastructure unless necessary.

---

# 35. SDK

After the API contracts are stable, create a minimal SIMORGH SDK abstraction.

Conceptually:

```python
client.ai.chat(...)
client.ai.embeddings(...)
client.knowledge.search(...)
client.audit.record(...)
client.notifications.send(...)
```

The SDK should:

* handle authentication
* handle request IDs
* standardize errors
* expose typed request/response models where practical
* avoid leaking provider-specific details

Applications should prefer SDK usage over raw HTTP.

---

# 36. COUNCIL INTEGRATION

The first integration target is the SIMORGH AI Management Council.

Refactor Council so that:

```text
Council
   ↓
SIMORGH SDK
   ↓
SIMORGH Platform API
   ↓
AI Gateway
   ↓
Provider
```

Council must NOT directly own LLM API credentials after migration.

Verify that existing Council behavior still works.

Do not break the Council UI/API contracts unnecessarily.

---

# 37. APPLICATION BOUNDARY

The following logic must remain OUTSIDE the Platform:

```text
Council debate algorithm
Council decision workflow
Product BOM
Product pricing
Production operations
Fleet maintenance
Order management
Customer-specific business rules
```

The Platform provides capabilities.

Applications compose those capabilities into business functionality.

---

# 38. TESTING

Create meaningful tests.

At minimum:

### Unit tests

* provider abstraction
* routing
* authentication
* authorization
* tenant isolation
* error handling
* usage calculation
* request ID propagation

### Integration tests

* AI endpoint
* provider adapter
* database
* knowledge endpoint
* audit endpoint

### Security tests

* cross-tenant access
* invalid credentials
* insufficient scope
* secret leakage
* malformed requests

### API contract tests

Validate request/response schemas.

Do not create meaningless tests that merely increase coverage numbers.

---

# 39. DOCUMENTATION

Update README with:

```text
What is SIMORGH Platform API?
Architecture
Quick Start
Environment Variables
Database Setup
Migration
Running the Server
API Documentation
Authentication
AI Providers
Routing
Knowledge
Audit
SDK
Testing
Deployment
Security
```

FastAPI OpenAPI documentation should work.

---

# 40. API CONTRACT DOCUMENT

Create a clear API contract document.

For every endpoint document:

```text
Method
Path
Purpose
Authentication
Required scopes
Request
Response
Errors
Example
```

Do not leave important behavior only inside code.

---

# 41. DEVELOPMENT PRINCIPLES

Follow these rules:

### Rule 1

Prefer simple architecture over clever architecture.

### Rule 2

Do not over-engineer for imaginary scale.

### Rule 3

Do not duplicate provider integrations.

### Rule 4

Do not leak provider-specific concepts into applications.

### Rule 5

Do not put business logic into Platform.

### Rule 6

Do not break existing working functionality without evidence.

### Rule 7

Every architectural abstraction must solve a real problem.

### Rule 8

Security boundaries must be explicit.

### Rule 9

Every important operation must be observable.

### Rule 10

The API contract is a product contract, not an implementation detail.

---

# 42. MVP SCOPE

The first implementation should prioritize:

```text
1. Platform foundation
2. Authentication
3. Application identity
4. Tenant context
5. AI Gateway
6. Provider abstraction
7. Model routing
8. AI usage tracking
9. Standard errors
10. Request tracing
11. Audit
12. Health
13. Knowledge foundation
14. Tests
15. Documentation
16. Council integration
```

Do NOT attempt to fully implement every future Platform feature in the first pass.

---

# 43. DEFERRED FEATURES

Unless the repository clearly requires them, defer:

```text
Kubernetes
Microservices
Kafka
Advanced distributed queues
Complex workflow engine
Advanced autonomous model routing
Full billing system
Enterprise IAM
Complex ABAC
Multi-region deployment
Distributed caching
Advanced vector infrastructure
Complex event bus
```

Build extension points, not premature infrastructure.

---

# 44. CODE QUALITY

Production-quality code is required.

Use:

* type hints
* Pydantic models
* dependency injection where appropriate
* clear module boundaries
* meaningful names
* small cohesive functions
* proper exception handling
* async where appropriate
* configuration management
* migrations
* tests

Avoid:

* giant files
* giant classes
* circular dependencies
* global mutable state
* duplicated provider logic
* hard-coded secrets
* hard-coded tenant IDs
* hidden magic behavior

---

# 45. IMPLEMENTATION WORKFLOW

Follow this exact workflow:

```text
PHASE 1
Repository Audit

↓

PHASE 2
Architecture Confirmation

↓

PHASE 3
API Contract

↓

PHASE 4
Database / Migration Design

↓

PHASE 5
Platform Foundation

↓

PHASE 6
Authentication + Tenant + Application Identity

↓

PHASE 7
AI Gateway

↓

PHASE 8
Provider Adapters

↓

PHASE 9
Routing + Usage

↓

PHASE 10
Knowledge Foundation

↓

PHASE 11
Audit + Events + Health

↓

PHASE 12
SDK

↓

PHASE 13
Council Integration

↓

PHASE 14
Tests

↓

PHASE 15
Documentation

↓

PHASE 16
Final Audit
```

---

# 46. AFTER EACH PHASE

After each major phase:

1. Run tests.
2. Check imports.
3. Check migrations.
4. Check API startup.
5. Check existing functionality.
6. Review security.
7. Review architecture.
8. Report what changed.

Do not continue while the project is knowingly broken.

---

# 47. FINAL VERIFICATION

At the end, verify:

```text
[ ] Server starts
[ ] Database connects
[ ] Migrations work
[ ] /health works
[ ] /ready works
[ ] Authentication works
[ ] Tenant isolation works
[ ] Application identity works
[ ] AI endpoint works
[ ] Provider abstraction works
[ ] Routing works
[ ] Usage is tracked
[ ] Errors are standardized
[ ] Request IDs propagate
[ ] Audit works
[ ] Knowledge foundation works
[ ] SDK works
[ ] Council integration works
[ ] Tests pass
[ ] OpenAPI is correct
[ ] README is updated
[ ] No secrets committed
[ ] No unnecessary infrastructure added
[ ] No application business logic leaked into Platform
```

---

# 48. FINAL REPORT

When implementation is complete, produce:

```text
SIMORGH PLATFORM — IMPLEMENTATION REPORT

1. What was implemented
2. Architecture
3. API endpoints
4. Database changes
5. Authentication model
6. Tenant model
7. AI providers
8. Routing strategy
9. Usage tracking
10. Knowledge implementation
11. Audit implementation
12. SDK
13. Council integration
14. Tests
15. Security review
16. Known limitations
17. Deferred work
18. How to run
19. How to test
20. Recommended next step
```

Also provide a list of every created/modified file:

```text
CREATED:
...

MODIFIED:
...

DELETED:
...
```

Do not claim a feature is implemented unless it actually exists and has been tested.

---

# 49. MOST IMPORTANT ARCHITECTURAL PRINCIPLE

The entire system must preserve this relationship:

```text
                    SIMORGH
                       │
          ┌────────────┴────────────┐
          │                         │
    Platform Capabilities      Applications
          │                         │
     HOW the system works      WHAT the business does
```

Platform:

```text
AI
Knowledge
Identity
Security
Audit
Runtime
Infrastructure
```

Application:

```text
Business meaning
Business rules
Business workflows
Business data
```

Never reverse these responsibilities.

---

# 50. EXECUTE

Now:

1. Inspect the repository.
2. Produce the initial repository audit.
3. Design the implementation against the actual repository.
4. Implement the MVP.
5. Run tests continuously.
6. Fix failures.
7. Integrate the Council.
8. Perform a final architecture/security review.
9. Produce the final implementation report.

Do not simply describe how to build it.

**Actually implement it in the repository.**

The final result must be a working, testable, documented **SIMORGH Platform API** that can serve as the shared API layer for the SIMORGH ecosystem.
