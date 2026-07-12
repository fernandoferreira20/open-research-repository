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
    assert isinstance(data, dict)
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 10
    assert data["pagination"]["total_items"] >= 2
    assert data["items"][0]["title"] == "Second Record"
    assert data["items"][1]["title"] == "First Record"


def test_list_records_supports_pagination_filter_search_and_sort(client):
    """GET /api/records should support page, per_page, status, q, sort, and order."""
    payloads = [
        make_record_payload(title="Alpha Paper", doi="10.1234/alpha", status="draft", record_type="paper"),
        make_record_payload(title="Beta Dataset", doi="10.1234/beta", status="published", record_type="dataset"),
        make_record_payload(title="Gamma Software", doi="10.1234/gamma", status="published", record_type="software"),
        make_record_payload(title="Delta Paper", doi="10.1234/delta", status="published", record_type="paper"),
    ]

    for payload in payloads:
        client.post("/api/records", json=payload)

    response = client.get(
        "/api/records",
        query_string={
            "page": "1",
            "per_page": "2",
            "status": "published",
            "q": "Paper",
            "sort": "title",
            "order": "asc",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 2
    assert data["pagination"]["total_items"] == 1
    assert data["pagination"]["total_pages"] == 1
    assert data["items"][0]["title"] == "Delta Paper"


def test_list_records_rejects_invalid_query_parameters(client):
    """GET /api/records should reject invalid query parameters with validation errors."""
    response = client.get(
        "/api/records",
        query_string={
            "page": "0",
            "per_page": "999",
            "record_type": "invalid",
            "sort": "invalid_field",
            "order": "up",
            "status": "unknown",
            "q": "x" * 201,
            "unknown": "value",
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "page" in data["error"]["details"]
    assert "per_page" in data["error"]["details"]
    assert "record_type" in data["error"]["details"]
    assert "sort" in data["error"]["details"]
    assert "order" in data["error"]["details"]
    assert "status" in data["error"]["details"]
    assert "q" in data["error"]["details"]
    assert "unknown" in data["error"]["details"]


def test_list_records_default_pagination(client):
    """GET /api/records should default to page 1 and per_page 10."""
    for idx in range(11):
        client.post(
            "/api/records",
            json=make_record_payload(title=f"Record {idx}", doi=f"10.1234/page{idx}"),
        )

    response = client.get("/api/records")
    assert response.status_code == 200

    data = response.get_json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 10
    assert data["pagination"]["total_items"] == 11
    assert data["pagination"]["total_pages"] == 2
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_previous"] is False
    assert len(data["items"]) == 10


def test_list_records_custom_pages(client):
    """GET /api/records should support custom page and per_page values."""
    for idx in range(7):
        client.post(
            "/api/records",
            json=make_record_payload(title=f"Page Record {idx}", doi=f"10.1234/custom{idx}"),
        )

    response1 = client.get("/api/records", query_string={"page": "1", "per_page": "3"})
    response2 = client.get("/api/records", query_string={"page": "2", "per_page": "3"})

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.get_json()
    data2 = response2.get_json()

    assert data1["pagination"]["page"] == 1
    assert data1["pagination"]["per_page"] == 3
    assert len(data1["items"]) == 3
    assert data1["pagination"]["has_next"] is True

    assert data2["pagination"]["page"] == 2
    assert data2["pagination"]["per_page"] == 3
    assert len(data2["items"]) == 3
    assert data2["pagination"]["has_previous"] is True


def test_list_records_filters_by_status(client):
    """GET /api/records should filter by status."""
    client.post("/api/records", json=make_record_payload(title="Draft Record", doi="10.1234/status1", status="draft"))
    client.post("/api/records", json=make_record_payload(title="Published Record", doi="10.1234/status2", status="published"))

    response = client.get("/api/records", query_string={"status": "published"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["total_items"] == 1
    assert data["items"][0]["status"] == "published"


def test_list_records_filters_by_record_type(client):
    """GET /api/records should filter by record_type."""
    client.post("/api/records", json=make_record_payload(title="Software Record", doi="10.1234/type1", record_type="software"))
    client.post("/api/records", json=make_record_payload(title="Paper Record", doi="10.1234/type2", record_type="paper"))

    response = client.get("/api/records", query_string={"record_type": "software"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["total_items"] == 1
    assert data["items"][0]["record_type"] == "software"


def test_list_records_searches_title_description_and_doi(client):
    """GET /api/records should search title, description, and DOI case-insensitively."""
    client.post("/api/records", json=make_record_payload(title="Unique Title", doi="10.1234/search", description="Common description"))
    client.post("/api/records", json=make_record_payload(title="Common Title", doi="10.1234/othersearch", description="Unique description"))

    title_search = client.get("/api/records", query_string={"q": "unique title"})
    description_search = client.get("/api/records", query_string={"q": "unique description"})
    doi_search = client.get("/api/records", query_string={"q": "10.1234/search"})

    assert title_search.status_code == 200
    assert description_search.status_code == 200
    assert doi_search.status_code == 200

    assert title_search.get_json()["pagination"]["total_items"] == 1
    assert description_search.get_json()["pagination"]["total_items"] == 1
    assert doi_search.get_json()["pagination"]["total_items"] == 1


def test_list_records_sorts_title_ascending(client):
    """GET /api/records should sort by title ascending."""
    client.post("/api/records", json=make_record_payload(title="Beta Title", doi="10.1234/sort1"))
    client.post("/api/records", json=make_record_payload(title="Alpha Title", doi="10.1234/sort2"))

    response = client.get("/api/records", query_string={"sort": "title", "order": "asc"})
    assert response.status_code == 200
    items = response.get_json()["items"]
    assert items[0]["title"] == "Alpha Title"
    assert items[1]["title"] == "Beta Title"


def test_list_records_combined_query(client):
    """GET /api/records should support combined filters, search, and sort."""
    client.post("/api/records", json=make_record_payload(title="Filter Match", doi="10.1234/combined1", status="published", record_type="paper"))
    client.post("/api/records", json=make_record_payload(title="Other Record", doi="10.1234/combined2", status="draft", record_type="paper"))
    client.post("/api/records", json=make_record_payload(title="Another Match", doi="10.1234/combined3", status="published", record_type="dataset"))

    response = client.get(
        "/api/records",
        query_string={
            "status": "published",
            "record_type": "paper",
            "q": "filter",
            "sort": "title",
            "order": "desc",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["total_items"] == 1
    assert data["items"][0]["title"] == "Filter Match"


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
