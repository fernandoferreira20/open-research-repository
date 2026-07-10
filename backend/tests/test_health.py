"""Health endpoint tests."""


def test_health_endpoint(client):
    """GET /api/health should return healthy status and service name."""
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()

    assert payload["status"] == "ok"
    assert payload["service"] == "open-research-repository-api"
