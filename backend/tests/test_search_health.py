"""Tests for the OpenSearch health endpoint and client initialization."""

import pytest

from flask import Flask
from opensearchpy import OpenSearch
from opensearchpy.exceptions import OpenSearchException

from app.search.client import get_opensearch_client, init_opensearch


def test_init_opensearch_stores_client_in_app_extensions():
    app = Flask(__name__)
    app.config["OPENSEARCH_URL"] = "http://localhost:9200"

    init_opensearch(app)

    assert "opensearch" in app.extensions
    assert isinstance(app.extensions["opensearch"], OpenSearch)


import pytest


def test_get_opensearch_client_without_app_context_raises_runtime_error(monkeypatch):
    monkeypatch.setattr("app.search.client.has_app_context", lambda: False)

    with pytest.raises(RuntimeError, match="active Flask application context"):
        get_opensearch_client()


def test_get_opensearch_client_before_init_raises_runtime_error():
    app = Flask(__name__)

    with app.app_context():
        with pytest.raises(RuntimeError, match="has not been initialized"):
            get_opensearch_client()


def test_search_health_ok(monkeypatch, client):
    class DummyClient:
        def ping(self):
            return True

    monkeypatch.setattr("app.search.routes.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok", "service": "opensearch"}


def test_search_health_unavailable_when_ping_false(monkeypatch, client):
    class DummyClient:
        def ping(self):
            return False

    monkeypatch.setattr("app.search.routes.client.get_opensearch_client", lambda: DummyClient())

    response = client.get("/api/search/health")

    assert response.status_code == 503
    data = response.get_json()
    assert data == {"status": "unavailable", "service": "opensearch"}


def test_search_health_unavailable_on_exception(monkeypatch, client):
    def failing_client():
        raise OpenSearchException("connection failed")

    monkeypatch.setattr("app.search.routes.client.get_opensearch_client", failing_client)

    response = client.get("/api/search/health")

    assert response.status_code == 503
    data = response.get_json()
    assert data == {"status": "unavailable", "service": "opensearch"}
