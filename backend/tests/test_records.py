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


def test_update_record_success(client):
    """PUT /api/records/<id> should update editable fields."""
    payload = make_record_payload(title="Initial Title", doi="10.1234/update1")
    post_response = client.post("/api/records", json=payload)
    record = post_response.get_json()
    record_id = record["id"]
    created_at = record["created_at"]
    original_updated_at = record["updated_at"]

    update_payload = {"title": "Updated Title", "status": "published"}

    response = client.put(f"/api/records/{record_id}", json=update_payload)
    assert response.status_code == 200

    updated = response.get_json()
    assert updated["id"] == record_id
    assert updated["title"] == "Updated Title"
    assert updated["status"] == "published"
    assert updated["created_at"] == created_at
    assert updated["updated_at"] != original_updated_at


def test_partial_update_record(client):
    """Partial update should change only provided fields."""
    payload = make_record_payload(title="Partial Title", doi="10.1234/partial")
    post_response = client.post("/api/records", json=payload)
    record = post_response.get_json()
    record_id = record["id"]

    update_payload = {"status": "published"}
    response = client.put(f"/api/records/{record_id}", json=update_payload)
    assert response.status_code == 200

    updated = response.get_json()
    assert updated["status"] == "published"
    assert updated["title"] == payload["title"]
    assert updated["description"] == payload["description"]
    assert updated["doi"] == payload["doi"]


def test_update_validation_errors(client):
    """Invalid update payload should return validation errors."""
    payload = make_record_payload(title="Bad Update", doi="10.1234/badupdate")
    post_response = client.post("/api/records", json=payload)
    record_id = post_response.get_json()["id"]

    response = client.put(f"/api/records/{record_id}", json={"record_type": "invalid"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "record_type" in data["error"]["details"]

    response = client.put(f"/api/records/{record_id}", json={"title": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "title" in data["error"]["details"]


def test_empty_update_body(client):
    """Empty update payload should return a validation error."""
    payload = make_record_payload(title="Empty Body", doi="10.1234/empty")
    record_id = client.post("/api/records", json=payload).get_json()["id"]

    response = client.put(f"/api/records/{record_id}", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"


def test_unknown_update_field(client):
    """Unknown update fields are rejected with validation error."""
    payload = make_record_payload(title="Unknown Field", doi="10.1234/unknown")
    record_id = client.post("/api/records", json=payload).get_json()["id"]

    response = client.put(f"/api/records/{record_id}", json={"unknown": "value"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "unknown" in data["error"]["details"]


def test_update_missing_record(client):
    """Updating a missing record should return 404."""
    response = client.put("/api/records/00000000-0000-0000-0000-000000000000", json={"title": "No Record"})
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"]["code"] == "not_found"


def test_update_duplicate_doi(client):
    """Updating a record to a duplicate DOI should return 409."""
    first = make_record_payload(title="First", doi="10.1234/firstdup")
    second = make_record_payload(title="Second", doi="10.1234/secondup")

    client.post("/api/records", json=first)
    second_id = client.post("/api/records", json=second).get_json()["id"]

    response = client.put(f"/api/records/{second_id}", json={"doi": "10.1234/firstdup"})
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"]["code"] == "conflict"
    assert "doi" in data["error"].get("details", {})


def test_delete_record_success(client):
    """DELETE /api/records/<id> should remove the record."""
    payload = make_record_payload(title="Delete Me", doi="10.1234/delete")
    record_id = client.post("/api/records", json=payload).get_json()["id"]

    delete_response = client.delete(f"/api/records/{record_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/records/{record_id}")
    assert get_response.status_code == 404


def test_delete_missing_record(client):
    """Deleting a missing record should return 404."""
    response = client.delete("/api/records/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"]["code"] == "not_found"
