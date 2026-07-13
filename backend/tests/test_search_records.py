"""Tests for the public OpenSearch-powered search endpoint."""

import pytest
from opensearchpy.exceptions import OpenSearchException


def make_search_query(**overrides):
    query = {
        "q": "important research",
        "page": "2",
        "per_page": "3",
        "status": "published",
        "record_type": "paper",
        "sort": "title",
        "order": "asc",
    }
    query.update(overrides)
    return query


def test_search_with_q_builds_multi_match_and_boosts_fields(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["index"] = index
            recorded["body"] = body
            return {
                "hits": {
                    "total": {"value": 0, "relation": "eq"},
                    "hits": [],
                }
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string=make_search_query())
    assert response.status_code == 200
    assert recorded["body"]["query"]["bool"]["must"][0]["multi_match"]["fields"] == ["title^3", "description", "doi^2"]
    assert recorded["body"]["sort"] == [{"title.keyword": {"order": "asc"}}]
    assert recorded["body"]["from"] == 3
    assert recorded["body"]["size"] == 3


def test_search_without_q_uses_match_all(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {
                    "total": {"value": 0, "relation": "eq"},
                    "hits": [],
                }
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={})
    assert response.status_code == 200
    assert recorded["body"]["query"]["bool"]["must"] == {"match_all": {}}
    assert recorded["body"]["sort"] == [{"created_at": {"order": "desc"}}]


def test_search_status_filter(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"status": "archived"})
    assert response.status_code == 200
    assert {"term": {"status": "archived"}} in recorded["body"]["query"]["bool"]["filter"]


def test_search_record_type_filter(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"record_type": "dataset"})
    assert response.status_code == 200
    assert {"term": {"record_type": "dataset"}} in recorded["body"]["query"]["bool"]["filter"]


def test_search_combined_filters(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get(
        "/api/search/records",
        query_string={"q": "doc", "status": "published", "record_type": "software"},
    )
    assert response.status_code == 200
    assert {"term": {"status": "published"}} in recorded["body"]["query"]["bool"]["filter"]
    assert {"term": {"record_type": "software"}} in recorded["body"]["query"]["bool"]["filter"]


def test_search_pagination_from_and_size(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 1, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"page": "3", "per_page": "20"})
    assert response.status_code == 200
    assert recorded["body"]["from"] == 40
    assert recorded["body"]["size"] == 20


def test_search_relevance_sorting_with_q(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 1, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"q": "test", "sort": "relevance"})
    assert response.status_code == 200
    assert recorded["body"]["sort"] == ["_score"]


def test_search_title_sorting_uses_keyword(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 1, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"sort": "title", "order": "asc"})
    assert response.status_code == 200
    assert recorded["body"]["sort"] == [{"title.keyword": {"order": "asc"}}]


def test_search_created_at_descending_sort(monkeypatch, client):
    recorded = {}

    class DummyClient:
        def search(self, index, body):
            recorded["body"] = body
            return {
                "hits": {"total": {"value": 1, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"sort": "created_at", "order": "desc"})
    assert response.status_code == 200
    assert recorded["body"]["sort"] == [{"created_at": {"order": "desc"}}]


def test_search_result_transformation_includes_score(monkeypatch, client):
    class DummyClient:
        def search(self, index, body):
            return {
                "hits": {
                    "total": {"value": 2, "relation": "eq"},
                    "hits": [
                        {"_source": {"id": "1", "title": "A"}, "_score": 1.2},
                        {"_source": {"id": "2", "title": "B"}, "_score": None},
                    ],
                }
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"page": "1", "per_page": "2"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["total_items"] == 2
    assert data["pagination"]["total_pages"] == 1
    assert data["items"][0]["score"] == 1.2
    assert data["items"][1]["score"] is None


def test_search_empty_results(monkeypatch, client):
    class DummyClient:
        def search(self, index, body):
            return {
                "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
            }

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"q": "missing"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == []
    assert data["pagination"]["total_items"] == 0
    assert data["pagination"]["total_pages"] == 0


def test_search_invalid_page_returns_400(client):
    response = client.get("/api/search/records", query_string={"page": "0"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "page" in data["error"]["details"]


def test_search_invalid_per_page_returns_400(client):
    response = client.get("/api/search/records", query_string={"per_page": "101"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "per_page" in data["error"]["details"]


def test_search_invalid_status_returns_400(client):
    response = client.get("/api/search/records", query_string={"status": "invalid"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "status" in data["error"]["details"]


def test_search_invalid_record_type_returns_400(client):
    response = client.get("/api/search/records", query_string={"record_type": "invalid"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "record_type" in data["error"]["details"]


def test_search_invalid_sort_returns_400(client):
    response = client.get("/api/search/records", query_string={"sort": "unknown"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "sort" in data["error"]["details"]


def test_search_invalid_order_returns_400(client):
    response = client.get("/api/search/records", query_string={"order": "up"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "order" in data["error"]["details"]


def test_search_unknown_parameter_returns_400(client):
    response = client.get("/api/search/records", query_string={"unknown": "value"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "unknown" in data["error"]["details"]


def test_search_query_too_long_returns_400(client):
    response = client.get("/api/search/records", query_string={"q": "x" * 201})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "validation_error"
    assert "q" in data["error"]["details"]


def test_search_returns_503_when_opensearch_unavailable(monkeypatch, client):
    def failing_client():
        raise OpenSearchException("connection failed")

    monkeypatch.setattr("app.search.routes.client.get_opensearch_client", failing_client)

    response = client.get("/api/search/records", query_string={"q": "test"})
    assert response.status_code == 503
    data = response.get_json()
    assert data["error"]["code"] == "search_unavailable"


def test_search_returns_500_on_unexpected_exception(monkeypatch, client):
    class DummyClient:
        def search(self, index, body):
            raise ValueError("boom")

    monkeypatch.setattr("app.search.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/records", query_string={"q": "test"})
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"]["code"] == "server_error"
    assert "boom" not in data["error"]["message"]
