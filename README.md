# Task API — FastAPI + PostgreSQL + JWT

A production-style REST API for task management, built with FastAPI, 
SQLAlchemy 2.0, and PostgreSQL. Implements stateless JWT authentication, 
per-user resource authorization, Docker deployment, and a full pytest suite.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-24%20passed-brightgreen?style=flat)

---

## Features

- **JWT Authentication** — stateless auth with signed tokens, bcrypt 
  password hashing, configurable expiration
- **Per-user Authorization** — every task is owner-scoped; cross-user 
  access returns 404 (not 403) by design
- **Full CRUD** — create, list, get, partial update (PATCH), and delete 
  tasks with status/priority enums
- **Query filters** — filter by status, include/exclude archived, 
  pagination with skip/limit validation
- **Auto-generated docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- **Docker-ready** — single `docker compose up` spins up API + database
- **24 automated tests** — covering auth flows, CRUD operations, 
  authorization boundaries, and edge cases

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (Mapped / mapped_column) |
| Database | PostgreSQL 16 |
| Auth | JWT via PyJWT + bcrypt |
| Validation | Pydantic v2 with EmailStr |
| Testing | pytest + httpx + SQLite in-memory |
| Deployment | Docker + docker-compose |

---

## Getting Started

### Option A — Docker (recommended)

No Python or PostgreSQL installation required.

```bash
git clone https://github.com/ambrociocastanazag-ctrl/task-api-fastapi.git
cd task-api-fastapi
docker compose up --build
```

API available at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

### Option B — Local development

**Prerequisites:** Python 3.12+, PostgreSQL 14+

```bash
# 1. Clone and create virtual environment
git clone https://github.com/ambrociocastanazag-ctrl/task-api-fastapi.git
cd task-api-fastapi
python -m venv .venv

# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials and JWT secret key

# 4. Start the API
uvicorn app.main:app --reload
```

### Environment variables

Copy `.env.example` to `.env` and fill in your values:

```ini
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/taskapi
JWT_SECRET_KEY=your-secret-key-here   # generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
DEBUG=True
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | Register new user |
| POST | `/auth/login` | None | Login, returns JWT token |
| GET | `/auth/me` | Bearer | Get current user profile |

### Tasks

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/tasks` | Bearer | Create task |
| GET | `/tasks` | Bearer | List own tasks (filterable) |
| GET | `/tasks/{id}` | Bearer | Get specific task |
| PATCH | `/tasks/{id}` | Bearer | Partial update |
| DELETE | `/tasks/{id}` | Bearer | Delete task |

### Query parameters for `GET /tasks`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | — | Filter by status: `pending`, `in_progress`, `done`, `cancelled` |
| `include_archived` | bool | `false` | Include archived tasks |
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `20` | Results per page (max 100) |

### Quick example

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"mypassword","full_name":"John Doe"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=user@example.com&password=mypassword"

# Create task (use token from login response)
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first task","status":"pending","priority":"high"}'
```

---

## Running Tests

Tests use SQLite in-memory via `dependency_overrides` — no database 
setup required.

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run the full suite
pytest

# Expected output
# 24 passed in ~4s
```

### What's tested

| Area | Tests |
|------|-------|
| Auth — register (success + validation + duplicate) | 4 |
| Auth — login (success + wrong password) | 2 |
| Auth — protected endpoints + invalid token | 3 |
| Task CRUD (create, list, get, update, delete) | 7 |
| Authorization (cross-user access returns 404) | 3 |
| Filters and pagination | 2 |
| Health check | 1 |

---

## Project Structure

```
task-api-fastapi/
├── app/
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── deps.py          # get_current_user dependency
│   │   └── security.py      # bcrypt hashing + JWT encode/decode
│   ├── models/
│   │   ├── user.py          # User ORM model
│   │   └── task.py          # Task ORM model + enums
│   ├── routes/
│   │   ├── auth.py          # /auth endpoints
│   │   ├── health.py        # /health endpoint
│   │   └── tasks.py         # /tasks CRUD endpoints
│   ├── schemas/
│   │   ├── user.py          # Pydantic schemas for User
│   │   └── task.py          # Pydantic schemas for Task
│   └── main.py              # App factory + router registration
├── tests/
│   ├── conftest.py          # Fixtures: DB, client, auth helpers
│   ├── test_auth.py         # Auth endpoint tests
│   ├── test_health.py       # Health check test
│   └── test_tasks.py        # CRUD + authorization tests
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

---

## Design Decisions

**404 instead of 403 for cross-user access**
When a user requests a task that belongs to someone else, the API returns 
404 Not Found instead of 403 Forbidden. This avoids leaking whether a 
resource ID exists at all — a standard security pattern for user-scoped APIs.

**PATCH over PUT for updates**
The update endpoint accepts partial payloads via Pydantic's 
`model_dump(exclude_unset=True)`. Only fields included in the request body 
are modified. Sending `{"status": "done"}` will not touch title or description.

**SQLite in-memory for tests**
Tests override FastAPI's `get_db` dependency to inject a SQLite in-memory 
session. This makes the test suite self-contained, fast (~4s for 24 tests), 
and runnable without any database setup.

---

## Author

**Gabriel Ambrocio** — Python Backend Developer  
Guatemala City, Guatemala (UTC-6)

[GitHub](https://github.com/ambrociocastanazag-ctrl) · 
[LinkedIn](https://www.linkedin.com/in/gabriel-omar-ambrocio-castañaza-a72a1a2b3) · 
ambrociocastanazag@gmail.com