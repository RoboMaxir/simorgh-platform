# SIMORGH PLATFORM API CONTRACT

## Overview

This document defines the official API contract for the SIMORGH Platform API v1.

All endpoints follow RESTful conventions and return consistent response formats.

---

## Base URL

```
Production: https://platform.simorgh.example/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All endpoints (except health checks) require authentication using HTTP Basic Auth:

```
Authorization: Basic base64(key_id:secret)
```

### Credentials

- `key_id`: Public identifier for the credential
- `secret`: Secret shown only at creation time

---

## Standard Response Format

### Success Response

```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "request_id": "uuid",
    "details": { ... }  // Optional
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | No credentials provided |
| `INVALID_CREDENTIALS` | 401 | Invalid key_id or secret |
| `INSUFFICIENT_SCOPE` | 403 | Credential lacks required scope |
| `TENANT_NOT_FOUND` | 404 | Tenant does not exist |
| `APPLICATION_NOT_FOUND` | 404 | Application does not exist |
| `PROVIDER_UNAVAILABLE` | 503 | No AI provider available |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INVALID_REQUEST` | 400 | Malformed request |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Endpoints

### Health Checks

#### GET /health

**Purpose:** Check if the process is alive

**Authentication:** None

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

#### GET /ready

**Purpose:** Check if all dependencies are ready

**Authentication:** None

**Response:**

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "ai_providers": "ok"
  }
}
```

---

### Authentication

#### POST /api/v1/auth/token

**Purpose:** Exchange credentials for a JWT access token (optional)

**Authentication:** Basic Auth (key_id:secret)

**Required Scopes:** None (credential validation only)

**Request:**

```json
{
  "expires_in": 3600  // Optional, seconds
}
```

**Response:**

```json
{
  "data": {
    "access_token": "jwt_token",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": ["ai.chat", "ai.embeddings"]
  }
}
```

---

### AI Gateway

#### POST /api/v1/ai/chat

**Purpose:** Send a chat completion request through the platform's AI gateway

**Authentication:** Required

**Required Scopes:** `ai.chat`

**Request:**

```json
{
  "model": "reasoning",
  "messages": [
    {
      "role": "user",
      "content": "Analyze this investment decision."
    }
  ],
  "temperature": 0.2,
  "max_tokens": 2000,
  "metadata": {
    "operation": "decision_analysis"
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| model | string | Yes | Logical model name (e.g., "reasoning", "fast") |
| messages | array | Yes | Array of message objects |
| messages[].role | string | Yes | "system", "user", or "assistant" |
| messages[].content | string | Yes | Message content |
| temperature | float | No | Sampling temperature (0.0-2.0), default 0.7 |
| max_tokens | integer | No | Maximum tokens to generate, default 1000 |
| metadata | object | No | Additional context for tracking |

**Response:**

```json
{
  "data": {
    "id": "chatcmpl-uuid",
    "model": "gpt-4",
    "provider": "openai",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "Based on the analysis..."
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 300,
      "total_tokens": 450
    },
    "latency_ms": 1250
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

---

#### POST /api/v1/ai/embeddings

**Purpose:** Generate embeddings for text inputs

**Authentication:** Required

**Required Scopes:** `ai.embeddings`

**Request:**

```json
{
  "model": "embedding",
  "input": [
    "First text to embed",
    "Second text to embed"
  ],
  "metadata": {
    "operation": "document_indexing"
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| model | string | Yes | Logical model name (e.g., "embedding") |
| input | array | Yes | Array of text strings |
| metadata | object | No | Additional context for tracking |

**Response:**

```json
{
  "data": {
    "model": "text-embedding-3-large",
    "provider": "openai",
    "embeddings": [
      {
        "index": 0,
        "embedding": [0.1, -0.2, 0.3, ...]
      },
      {
        "index": 1,
        "embedding": [0.4, -0.5, 0.6, ...]
      }
    ],
    "usage": {
      "prompt_tokens": 50,
      "total_tokens": 50
    },
    "latency_ms": 450
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

---

#### GET /api/v1/ai/models

**Purpose:** List available logical models

**Authentication:** Required

**Required Scopes:** `ai.models.read`

**Response:**

```json
{
  "data": [
    {
      "name": "reasoning",
      "description": "High-quality reasoning model for complex analysis",
      "capabilities": ["chat", "analysis", "reasoning"],
      "context_window": 200000
    },
    {
      "name": "fast",
      "description": "Fast, cost-effective model for simple tasks",
      "capabilities": ["chat", "summarization"],
      "context_window": 128000
    },
    {
      "name": "embedding",
      "description": "Embedding model for vector representations",
      "capabilities": ["embeddings"],
      "dimensions": 3072
    }
  ]
}
```

---

#### GET /api/v1/ai/providers

**Purpose:** List configured AI providers

**Authentication:** Required

**Required Scopes:** `ai.models.read`

**Response:**

```json
{
  "data": [
    {
      "name": "openai",
      "type": "openai",
      "status": "active",
      "models": ["gpt-4", "gpt-4o-mini", "text-embedding-3-large"]
    },
    {
      "name": "openai-compatible",
      "type": "openai-compatible",
      "status": "active",
      "endpoint": "https://qwen.example.com/v1",
      "models": ["qwen-max", "qwen-plus"]
    }
  ]
}
```

---

#### GET /api/v1/ai/usage

**Purpose:** Get AI usage statistics for the current tenant/application

**Authentication:** Required

**Required Scopes:** `ai.usage.read`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| from | date | Start date (ISO 8601) |
| to | date | End date (ISO 8601) |
| application_id | uuid | Filter by application (optional) |

**Response:**

```json
{
  "data": {
    "period": {
      "from": "2024-01-01T00:00:00Z",
      "to": "2024-01-31T23:59:59Z"
    },
    "summary": {
      "total_requests": 1500,
      "total_tokens": 450000,
      "total_cost_usd": 12.50
    },
    "by_provider": [
      {
        "provider": "openai",
        "requests": 1200,
        "tokens": 380000,
        "cost_usd": 10.20
      }
    ],
    "by_model": [
      {
        "model": "gpt-4",
        "requests": 800,
        "tokens": 300000,
        "cost_usd": 8.50
      }
    ],
    "by_operation": [
      {
        "operation": "chat",
        "requests": 1400,
        "tokens": 420000
      }
    ]
  }
}
```

---

### Knowledge

#### POST /api/v1/knowledge/search

**Purpose:** Search the knowledge base

**Authentication:** Required

**Required Scopes:** `knowledge.search`

**Request:**

```json
{
  "query": "What are the previous decisions about this investment?",
  "top_k": 5,
  "filters": {
    "source": "council",
    "created_after": "2024-01-01T00:00:00Z"
  }
}
```

**Response:**

```json
{
  "data": {
    "results": [
      {
        "id": "doc-uuid",
        "score": 0.95,
        "content": "The council decided to approve...",
        "metadata": {
          "source": "council",
          "created_at": "2024-01-15T10:30:00Z"
        }
      }
    ]
  }
}
```

---

#### POST /api/v1/knowledge/retrieve

**Purpose:** Retrieve a specific document by ID

**Authentication:** Required

**Required Scopes:** `knowledge.retrieve`

**Request:**

```json
{
  "document_id": "doc-uuid"
}
```

**Response:**

```json
{
  "data": {
    "id": "doc-uuid",
    "content": "Full document content...",
    "metadata": {
      "source": "council",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

---

#### POST /api/v1/knowledge/index

**Purpose:** Index a new document in the knowledge base

**Authentication:** Required

**Required Scopes:** `knowledge.write`

**Request:**

```json
{
  "content": "Document content to index...",
  "metadata": {
    "source": "council",
    "title": "Investment Decision #123"
  }
}
```

**Response:**

```json
{
  "data": {
    "id": "doc-uuid",
    "status": "indexed"
  }
}
```

---

### Audit

#### POST /api/v1/audit/events

**Purpose:** Record an audit event

**Authentication:** Required

**Required Scopes:** `audit.write`

**Request:**

```json
{
  "action": "DECISION_CREATED",
  "resource": "council.decision",
  "resource_id": "decision-uuid",
  "metadata": {
    "decision_type": "investment",
    "amount": 1000000
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | Yes | Action performed (e.g., CREATE, UPDATE, DELETE) |
| resource | string | Yes | Resource type (e.g., "council.decision") |
| resource_id | string | Yes | Resource identifier |
| metadata | object | No | Additional context |

**Note:** `tenant_id`, `application_id`, `actor_id`, and `request_id` are automatically populated from the authenticated context.

**Response:**

```json
{
  "data": {
    "id": "audit-uuid",
    "status": "recorded"
  }
}
```

---

#### GET /api/v1/audit/events

**Purpose:** Query audit events

**Authentication:** Required

**Required Scopes:** `audit.read`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| resource | string | Filter by resource type |
| resource_id | string | Filter by resource ID |
| action | string | Filter by action |
| from | date | Start date (ISO 8601) |
| to | date | End date (ISO 8601) |
| limit | integer | Max results (default 100, max 1000) |
| offset | integer | Pagination offset |

**Response:**

```json
{
  "data": [
    {
      "id": "audit-uuid",
      "tenant_id": "tenant-uuid",
      "application_id": "app-uuid",
      "actor_id": "user-uuid",
      "action": "DECISION_CREATED",
      "resource": "council.decision",
      "resource_id": "decision-uuid",
      "request_id": "req-uuid",
      "metadata": {
        "decision_type": "investment",
        "amount": 1000000
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 150,
    "limit": 100,
    "offset": 0
  }
}
```

---

## Rate Limiting

Rate limits are applied per credential:

| Tier | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Default | 60 | 10,000 |
| Elevated | 300 | 100,000 |

Rate limit headers included in responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704067200
```

---

## Versioning

All API endpoints are versioned:

```
/api/v1/*
```

Breaking changes will result in a new major version:

```
/api/v2/*
```

Non-breaking additions may be made to v1 endpoints.

---

## OpenAPI Documentation

Interactive API documentation is available at:

```
Development: http://localhost:8000/docs
Production: https://platform.simorgh.example/docs
```

ReDoc documentation:

```
Development: http://localhost:8000/redoc
```

---

## SDK Usage

Applications should use the official SIMORGH SDK instead of making raw HTTP requests:

```python
from simorgh_sdk import SimorghClient

client = SimorghClient(
    base_url="http://localhost:8000",
    key_id="your-key-id",
    secret="your-secret"
)

# Chat completion
response = await client.ai.chat(
    model="reasoning",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Knowledge search
results = await client.knowledge.search(
    query="previous decisions",
    top_k=5
)

# Record audit event
await client.audit.record(
    action="DECISION_CREATED",
    resource="council.decision",
    resource_id="decision-uuid"
)
```

---

*Last updated: 2024-01-01*
*Version: 1.0.0*
