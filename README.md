# Task API

REST API for task management built with **FastAPI**, **PostgreSQL** and **SQLAlchemy**.

> 🚧 In active development — JWT authentication, full CRUD endpoints and Docker setup land on day 2.

## Stack

- FastAPI 0.115
- SQLAlchemy 2.0
- PostgreSQL 16
- Pydantic v2

## Quick start (local)

```bash
# 1. Clone and enter the repo
git clone https://github.com/<your-user>/task-api-fastapi.git
cd task-api-fastapi

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Run the server
uvicorn app.main:app --reload
```

Interactive API docs at http://localhost:8000/docs

## Project structure

```
app/
├── main.py          # FastAPI app entry point
├── config.py        # Settings (pydantic-settings)
├── database.py      # SQLAlchemy engine & session
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
└── routes/          # API endpoints
tests/               # Pytest test suite
```

## Roadmap

- [x] Project scaffolding
- [ ] Task CRUD endpoints
- [ ] JWT authentication
- [ ] Docker & docker-compose setup
- [ ] Pytest test coverage

## License

MIT
