# Multi-Tenant Organization Manager Backend

A backend API built with **FastAPI** that supports multi-tenant organizations with JWT authentication, role-based access control, audit logging, and an AI chatbot for activity analysis.

## Architecture

The project follows **Clean / Layered Architecture** with four clearly separated layers:

```
Client (HTTP)
     │
     ▼
┌─────────────┐
│  API Layer   │  FastAPI routers (auth, organizations, items, audit_logs)
└──────┬──────┘
       │
┌──────▼──────┐
│Service Layer │  Business logic, validation, orchestration
└──────┬──────┘
       │
┌──────▼──────┐
│  Repository  │  Async SQLAlchemy queries
│    Layer     │
└──────┬──────┘
       │
┌──────▼──────┐
│  PostgreSQL  │
└─────────────┘
```

### Folder Structure

```
app/
 ├── main.py                 # FastAPI entry point
 ├── api/                    # Route handlers
 │   ├── auth.py
 │   ├── organizations.py
 │   ├── items.py
 │   └── audit_logs.py
 ├── core/                   # Config, security, dependencies
 │   ├── config.py
 │   ├── security.py
 │   └── dependencies.py
 ├── db/                     # Database engine & base
 │   ├── session.py
 │   └── base.py
 ├── models/                 # SQLAlchemy ORM models
 │   ├── user.py
 │   ├── organization.py
 │   ├── membership.py
 │   ├── item.py
 │   └── audit_log.py
 ├── schemas/                # Pydantic request/response models
 │   ├── auth.py
 │   ├── user.py
 │   ├── organization.py
 │   ├── item.py
 │   └── audit_log.py
 ├── services/               # Business logic
 │   ├── auth_service.py
 │   ├── organization_service.py
 │   ├── item_service.py
 │   └── audit_service.py
 └── repositories/           # Data access
     ├── user_repo.py
     ├── org_repo.py
     ├── item_repo.py
     └── audit_repo.py
```

## Database Design (ER Diagram)

```mermaid
erDiagram
    User ||--o{ Membership : has
    Organization ||--o{ Membership : has
    Organization ||--o{ Item : contains
    Organization ||--o{ AuditLog : tracks
    User ||--o{ Item : creates
    User ||--o{ AuditLog : performs

    User {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        datetime created_at
    }
    Organization {
        uuid id PK
        string name
        uuid created_by FK
        datetime created_at
    }
    Membership {
        uuid id PK
        uuid user_id FK
        uuid org_id FK
        string role
        datetime created_at
    }
    Item {
        uuid id PK
        uuid org_id FK
        uuid created_by FK
        jsonb details
        datetime created_at
    }
    AuditLog {
        uuid id PK
        uuid org_id FK
        uuid user_id FK
        string action
        jsonb metadata
        datetime created_at
    }
```

## API Endpoints

| Method | Endpoint | Auth | Access | Description |
|--------|---------|------|--------|-------------|
| POST | `/auth/register` | - | Public | Register a new user |
| POST | `/auth/login` | - | Public | Login and get JWT token |
| POST | `/organizations` | JWT | Any user | Create organization |
| POST | `/organizations/{org_id}/users` | JWT | Admin | Invite user to org |
| GET | `/organizations/{org_id}/users` | JWT | Admin | List org users |
| GET | `/organizations/{org_id}/users/search?q=` | JWT | Admin | Full-text search users |
| POST | `/organizations/{org_id}/items` | JWT | Member+ | Create item |
| GET | `/organizations/{org_id}/items` | JWT | Member+ | List items (admin=all, member=own) |
| GET | `/organizations/{org_id}/audit-logs` | JWT | Admin | View audit logs |
| POST | `/organizations/{org_id}/audit-logs/ask` | JWT | Admin | AI chatbot for audit analysis |

## How to Run

### Prerequisites

- Docker and Docker Compose installed

### Quick Start

```bash
docker compose up
```

The API will be available at `http://localhost:8000`.

API documentation (Swagger UI) is at `http://localhost:8000/docs`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@postgres:5432/multi_tenant` | PostgreSQL connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration time |
| `LLM_PROVIDER` | `openai` | AI provider: `openai`, `gemini`, or `claude` |
| `LLM_API_KEY` | (empty) | API key for the chosen LLM provider |

### Running Tests

Tests use `testcontainers` which requires Docker to be running:

```bash
pip install -r requirements.txt
pytest
```

## Design Tradeoffs

1. **Async SQLAlchemy** -- Full async stack (asyncpg + async sessions) for non-blocking I/O. Adds complexity over sync but necessary for high-concurrency FastAPI workloads.

2. **JSONB for Item details** -- Flexible schema-less storage. Trades type safety for adaptability across different item types without schema migrations.

3. **JWT stateless auth** -- No server-side session storage needed, simplifies horizontal scaling. Tradeoff: tokens cannot be revoked until expiry (acceptable for this scope).

4. **PostgreSQL Full-Text Search** -- Uses `to_tsvector`/`to_tsquery` with GIN index instead of external search engines (Elasticsearch). Simpler infrastructure at the cost of advanced search features.

5. **LLM provider abstraction** -- Strategy pattern supports OpenAI, Gemini, and Claude via config. Avoids vendor lock-in while keeping the interface clean.

6. **Clean Architecture layers** -- Repositories encapsulate DB access, services own business logic, API routes handle HTTP concerns. More files but clear separation of concerns and testability.

7. **Alembic migrations** -- Versioned schema changes for production safety. The initial migration is hand-written to include the GIN full-text index.
