import pytest


# ───────────────────────────────────────────────────────────────
#  Helper: payload de task estándar
# ───────────────────────────────────────────────────────────────

@pytest.fixture
def task_payload():
    """Datos válidos de una task de prueba."""
    return {
        "title": "Sample task",
        "description": "Something to do",
        "status": "pending",
        "priority": "medium",
    }


# ───────────────────────────────────────────────────────────────
#  CRUD básico
# ───────────────────────────────────────────────────────────────

def test_create_task_success(client, auth_headers, task_payload):
    """Crear una task devuelve 201 con los datos correctos."""
    response = client.post("/tasks", json=task_payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_payload["title"]
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert data["is_archived"] is False
    assert "id" in data
    assert "owner_id" in data


def test_create_task_requires_auth(client, task_payload):
    """Sin token, no se puede crear una task."""
    response = client.post("/tasks", json=task_payload)
    assert response.status_code == 401


def test_list_tasks_returns_only_own_tasks(
    client, auth_headers, other_user_headers, task_payload
):
    """
    Cada usuario solo ve sus propias tasks.
    Validación crítica de autorización.
    """
    # User1 crea una task
    client.post("/tasks", json=task_payload, headers=auth_headers)

    # User2 crea otra task con título distinto
    other_payload = {**task_payload, "title": "Task de otro usuario"}
    client.post("/tasks", json=other_payload, headers=other_user_headers)

    # User1 lista sus tasks: solo debe ver la suya
    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == task_payload["title"]


def test_get_task_by_id(client, auth_headers, task_payload):
    """GET /tasks/{id} devuelve la task específica."""
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_nonexistent_task_returns_404(client, auth_headers):
    """Una task que no existe devuelve 404."""
    response = client.get("/tasks/99999", headers=auth_headers)
    assert response.status_code == 404


# ───────────────────────────────────────────────────────────────
#  Update parcial (PATCH)
# ───────────────────────────────────────────────────────────────

def test_patch_only_updates_provided_fields(client, auth_headers, task_payload):
    """
    Un PATCH con solo {status} no debe borrar title ni description.
    Validación crítica de PATCH vs PUT.
    """
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]
    original_title = create_response.json()["title"]
    original_description = create_response.json()["description"]

    # Solo actualizamos status
    patch_response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "done"},
        headers=auth_headers,
    )

    assert patch_response.status_code == 200
    updated = patch_response.json()
    assert updated["status"] == "done"
    # title y description NO deben haber cambiado
    assert updated["title"] == original_title
    assert updated["description"] == original_description


def test_patch_invalid_status_returns_422(client, auth_headers, task_payload):
    """Un status que no está en el enum debe ser rechazado."""
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "totally_invalid_value"},
        headers=auth_headers,
    )
    assert response.status_code == 422


# ───────────────────────────────────────────────────────────────
#  Delete
# ───────────────────────────────────────────────────────────────

def test_delete_task_returns_204(client, auth_headers, task_payload):
    """DELETE de una task existente devuelve 204 No Content."""
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204
    # 204 No Content significa que NO debe haber body
    assert response.content == b""


def test_deleted_task_is_gone(client, auth_headers, task_payload):
    """Después de DELETE, la task ya no debe ser accesible."""
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    client.delete(f"/tasks/{task_id}", headers=auth_headers)
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404


# ───────────────────────────────────────────────────────────────
#  Autorización entre usuarios
# ───────────────────────────────────────────────────────────────

def test_cannot_access_other_users_task(
    client, auth_headers, other_user_headers, task_payload
):
    """
    Un usuario no puede acceder a una task de otro usuario.
    Devuelve 404 (no 403) por seguridad — no revelamos que existe.
    """
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    # User2 intenta acceder a la task de User1
    response = client.get(f"/tasks/{task_id}", headers=other_user_headers)
    assert response.status_code == 404


def test_cannot_update_other_users_task(
    client, auth_headers, other_user_headers, task_payload
):
    """Un usuario no puede modificar la task de otro."""
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "done"},
        headers=other_user_headers,
    )
    assert response.status_code == 404


def test_cannot_delete_other_users_task(
    client, auth_headers, other_user_headers, task_payload
):
    """Un usuario no puede eliminar la task de otro."""
    create_response = client.post("/tasks", json=task_payload, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=other_user_headers)
    assert response.status_code == 404


# ───────────────────────────────────────────────────────────────
#  Filtros y paginación
# ───────────────────────────────────────────────────────────────

def test_filter_by_status(client, auth_headers, task_payload):
    """El query param ?status filtra tasks por estado."""
    # Crea 3 tasks con distintos status
    client.post("/tasks", json={**task_payload, "status": "pending"}, headers=auth_headers)
    client.post("/tasks", json={**task_payload, "status": "done"}, headers=auth_headers)
    client.post("/tasks", json={**task_payload, "status": "done"}, headers=auth_headers)

    response = client.get("/tasks?status=done", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert all(t["status"] == "done" for t in tasks)


def test_pagination_limit_works(client, auth_headers, task_payload):
    """El query param ?limit limita el número de resultados."""
    for i in range(5):
        client.post(
            "/tasks",
            json={**task_payload, "title": f"Task {i}"},
            headers=auth_headers,
        )

    response = client.get("/tasks?limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2