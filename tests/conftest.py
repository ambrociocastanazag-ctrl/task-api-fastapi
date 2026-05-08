"""
Configuración global de pytest: fixtures compartidas entre todos los tests.
Las fixtures definidas aquí están disponibles en cualquier test_*.py automáticamente.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


# ───────────────────────────────────────────────────────────────
#  Test Database — SQLite en memoria, aislada por test
# ───────────────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_engine():
    """
    Crea un engine de SQLite en memoria.
    StaticPool comparte la misma conexión entre threads — necesario
    porque TestClient corre el handler en otro thread.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Devuelve una sesión SQLAlchemy fresca para cada test."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ───────────────────────────────────────────────────────────────
#  Test Client — FastAPI con la DB de tests inyectada
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def client(db_engine):
    """
    Cliente HTTP de prueba con override de get_db
    para que use la DB en memoria en lugar de Postgres real.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ───────────────────────────────────────────────────────────────
#  Fixtures de usuarios autenticados
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def test_user_data():
    """Datos del usuario de prueba estándar."""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Registra un usuario y devuelve su data."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_token(client, registered_user, test_user_data):
    """Hace login y devuelve el JWT token listo para usar."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Devuelve los headers HTTP con el Bearer token, listos para usar en requests."""
    return {"Authorization": f"Bearer {auth_token}"}


# ───────────────────────────────────────────────────────────────
#  Fixture: segundo usuario (para tests de autorización cruzada)
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def other_user_headers(client):
    """
    Crea un segundo usuario y devuelve sus headers de autenticación.
    Útil para verificar que un usuario NO puede acceder a recursos de otro.
    """
    other_data = {
        "email": "other@example.com",
        "password": "otherpass456",
        "full_name": "Other User",
    }
    client.post("/auth/register", json=other_data)
    response = client.post(
        "/auth/login",
        data={
            "username": other_data["email"],
            "password": other_data["password"],
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}