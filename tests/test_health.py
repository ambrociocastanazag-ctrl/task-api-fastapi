def test_health_check_returns_ok(client):
    """El endpoint de health debe responder 200 con api y database en ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "ok"
    assert data["database"] == "ok"