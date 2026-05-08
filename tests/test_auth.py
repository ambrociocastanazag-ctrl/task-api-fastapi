def test_register_success(client, test_user_data):
    """Un registro válido devuelve 201 con datos del usuario sin password."""
    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    # Crítico: la API NUNCA debe devolver el password ni el hash
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client, registered_user, test_user_data):
    """Registrar el mismo email dos veces devuelve 409 Conflict."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_email_fails(client):
    """Email mal formado devuelve 422 Unprocessable Entity."""
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "pass12345", "full_name": "User"},
    )
    assert response.status_code == 422


def test_register_short_password_fails(client):
    """Password con menos de 8 caracteres devuelve 422."""
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "short", "full_name": "User"},
    )
    assert response.status_code == 422


def test_login_success(client, registered_user, test_user_data):
    """Login con credenciales correctas devuelve un access_token."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 50  # JWT tokens son largos


def test_login_wrong_password_fails(client, registered_user, test_user_data):
    """Login con password incorrecta devuelve 401 Unauthorized."""
    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "completely-wrong-password",
        },
    )
    assert response.status_code == 401


def test_me_endpoint_requires_auth(client):
    """Sin token, /auth/me devuelve 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_endpoint_returns_current_user(client, auth_headers, test_user_data):
    """Con token válido, /auth/me devuelve los datos del usuario actual."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]


def test_invalid_token_returns_401(client):
    """Un token mal formado o inválido devuelve 401."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer this-is-not-a-valid-jwt"},
    )
    assert response.status_code == 401