"""Tests for research record endpoints."""

from datetime import date


def make_record_payload(**overrides):
    """Return a valid record payload with optional overrides."""
    payload = {
        "title": "Sample Research",
        "description": "A good description.",
        "record_type": "paper",
        "status": "draft",
        "license": "CC BY 4.0",
        "doi": "10.1234/example",
        "publication_date": "2026-07-10",
    }
    payload.update(overrides)
    return payload


def test_create_valid_record(client):
    """POST /api/records should create a record and return 201."""
    payload = make_record_payload(status=None)
    payload.pop("status")

    response = client.post("/api/records", json=payload)

    assert response.status_code == 201
    data = response.get_json()

    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["status"] == "draft"
    assert data["publication_date"] == payload["publication_date"]


def test_validation_errors_for_required_fields(client):
    """Required fields should return validation_error details."""
    response = client.post("/api/records", json={})

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "title" in data["error"]["details"]
    assert "description" in data["error"]["details"]
    assert "record_type" in data["error"]["details"]


def test_validation_error_for_invalid_record_type(client):
    """Invalid record_type returns validation_error."""
    payload = make_record_payload(record_type="invalid")

    response = client.post("/api/records", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "record_type" in data["error"]["details"]


def test_list_records_ordered_newest_first(client):
    """GET /api/records should return records ordered by newest first."""
    first = make_record_payload(title="First Record", doi="10.1234/first")
    second = make_record_payload(title="Second Record", doi="10.1234/second")

    client.post("/api/records", json=first)
    client.post("/api/records", json=second)

    response = client.get("/api/records")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert data[0]["title"] == "Second Record"
    assert data[1]["title"] == "First Record"


def test_get_record_by_id(client):
    """GET /api/records/<id> should return the created record."""
    payload = make_record_payload(title="Findable Record", doi="10.1234/findable")
    post_response = client.post("/api/records", json=payload)
    record_id = post_response.get_json()["id"]

    get_response = client.get(f"/api/records/{record_id}")
    assert get_response.status_code == 200

    data = get_response.get_json()
    assert data["id"] == record_id
    assert data["title"] == payload["title"]


def test_get_record_not_found(client):
    """Requesting a missing record should return 404."""
    response = client.get("/api/records/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"]["code"] == "not_found"


def test_duplicate_doi_conflict(client):
    """Creating two records with the same DOI should return a 409 conflict."""
    payload = make_record_payload(doi="10.1234/duplicate")
    client.post("/api/records", json=payload)

    second_response = client.post("/api/records", json=payload)
    assert second_response.status_code == 409

    data = second_response.get_json()
    assert data["error"]["code"] == "conflict"
    assert "doi" in data["error"].get("details", {})
