# SIMORGH Platform Frontend API Mapping

Branch: rbac-access-relationship-reform-74b9c

Backend is the source of truth.

| Feature | Method | Endpoint | Auth / scope | Status |
|---|---|---|---|---|
| Human login | POST | /api/v1/auth/login | Public | IMPLEMENTED |
| Machine token exchange | POST | /api/v1/auth/token | Basic key_id:secret | PLACEHOLDER UI |
| AI chat | POST | /api/v1/ai/chat | Bearer, context-dependent | IMPLEMENTED |
| Embeddings | POST | /api/v1/ai/embeddings | Bearer, context-dependent | IMPLEMENTED |
| AI models | GET | /api/v1/ai/models | Public | IMPLEMENTED |
| AI providers | GET | /api/v1/ai/providers | Public | IMPLEMENTED |
| AI usage | GET | /api/v1/ai/usage | Bearer, context-dependent | PARTIAL |
| Knowledge index | POST | /api/v1/knowledge/index | knowledge.write | PLACEHOLDER |
| Knowledge search | POST | /api/v1/knowledge/search | knowledge.search | PLACEHOLDER |
| Knowledge document | GET | /api/v1/knowledge/documents/{document_id} | knowledge.retrieve | IMPLEMENTED |
| Audit events | GET | /api/v1/audit/events | audit.read | PLACEHOLDER |
| Audit event | POST | /api/v1/audit/events | audit.write | PLACEHOLDER |
| Health | GET | /api/v1/health | Public | IMPLEMENTED |
| Readiness | GET | /api/v1/ready | Public | IMPLEMENTED |
| Applications | — | — | — | BACKEND_MISSING |
| Credentials CRUD | — | — | — | BACKEND_MISSING |
| Billing / credits | — | — | — | BACKEND_MISSING |
| Users/workspaces/roles/permissions CRUD | — | — | — | BACKEND_MISSING |

## Contract finding

The human login JWT contains user_id, workspace_id, email, name and is_superuser. The protected AI/knowledge/audit dependencies require tenant_id, application_id and scopes. The frontend does not fabricate those claims. Until the backend aligns the human dashboard context with those dependencies, protected usage/knowledge/audit calls may return authentication or authorization errors.

## Data states

LIVE = direct backend data. UNAVAILABLE = current API cannot provide it. BACKEND_MISSING = no corresponding route verified. PLACEHOLDER = endpoint exists but backend explicitly returns placeholder behavior.
