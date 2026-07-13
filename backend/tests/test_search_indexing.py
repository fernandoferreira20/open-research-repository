"""Unit tests for OpenSearch record indexing helpers."""

import pytest
from opensearchpy.exceptions import NotFoundError

from app.search.index import DEFAULT_RECORDS_INDEX, INDEX_BODY, research_record_to_document
from app.search.services import (
    _resolve_records_index_name,
    create_records_index,
    delete_records_index,
    delete_research_record_document,
    ensure_records_index,
    index_exists,
    index_research_record,
    rebuild_records_index,
    update_research_record_document,
)


class DummyRecord:
    def __init__(self):
        self.id = "12345"
        self.title = "Test Title"
        self.description = "Test description"
        self.record_type = "paper"
        self.status = "draft"
        self.license = "CC BY 4.0"
        self.doi = "10.1234/test"
        self.publication_date = None
        self.created_at = None
        self.updated_at = None


class DummyClient:
    def __init__(self):
        self.calls = []

    def index(self, *, index, id, body, refresh):
        self.calls.append(("index", index, id, body, refresh))
        return {"result": "created", "_id": id}

    def delete(self, *, index, id, refresh):
        self.calls.append(("delete", index, id, refresh))
        return {"result": "deleted"}


class DummyMissingClient(DummyClient):
    def delete(self, *, index, id, refresh):
        self.calls.append(("delete", index, id, refresh))
        raise NotFoundError("not found")


def test_research_record_to_document_serializes_fields():
    record = DummyRecord()

    document = research_record_to_document(record)

    assert document["id"] == "12345"
    assert document["title"] == "Test Title"
    assert document["description"] == "Test description"
    assert document["record_type"] == "paper"
    assert document["status"] == "draft"
    assert document["license"] == "CC BY 4.0"
    assert document["doi"] == "10.1234/test"
    assert document["publication_date"] is None
    assert document["created_at"] is None
    assert document["updated_at"] is None


def test_resolve_records_index_name_uses_config_value():
    config = {"OPENSEARCH_RECORDS_INDEX": "custom_records"}

    assert _resolve_records_index_name(config) == "custom_records"


def test_resolve_records_index_name_falls_back_to_default():
    assert _resolve_records_index_name({}) == DEFAULT_RECORDS_INDEX
    assert _resolve_records_index_name(None) == DEFAULT_RECORDS_INDEX


def test_index_exists_returns_true_when_index_present():
    client = DummyClient()
    client.indices = type("Indices", (), {"exists": lambda self, index: True})()

    assert index_exists(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"}) is True


def test_index_exists_returns_false_when_index_missing():
    client = DummyClient()
    client.indices = type("Indices", (), {"exists": lambda self, index: False})()

    assert index_exists(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"}) is False


def test_create_records_index_creates_index_when_missing():
    client = DummyClient()
    client.indices = type("Indices", (), {"exists": lambda self, index: False, "create": lambda self, index, body: client.calls.append(("create", index, body))})()

    created = ensure_records_index(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert created is True
    assert client.calls == [("create", "custom_records", INDEX_BODY)]


def test_create_records_index_returns_false_when_index_exists():
    client = DummyClient()
    client.indices = type("Indices", (), {"exists": lambda self, index: True, "create": lambda self, index, body: client.calls.append(("create", index, body))})()

    created = create_records_index(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert created is False
    assert client.calls == []


def test_delete_records_index_returns_true_when_present():
    client = DummyClient()
    client.indices = type(
        "Indices",
        (),
        {
            "exists": lambda self, index: True,
            "delete": lambda self, index: client.calls.append(("delete_index", index)),
        },
    )()

    deleted = delete_records_index(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert deleted is True
    assert client.calls == [("delete_index", "custom_records")]


def test_delete_records_index_returns_false_when_absent():
    client = DummyClient()
    client.indices = type(
        "Indices",
        (),
        {
            "exists": lambda self, index: False,
            "delete": lambda self, index: client.calls.append(("delete_index", index)),
        },
    )()

    deleted = delete_records_index(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert deleted is False
    assert client.calls == []


def test_index_research_record_calls_client_index_with_serialized_document():
    client = DummyClient()
    record = DummyRecord()

    response = index_research_record(client, record, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert response["result"] == "created"
    assert client.calls == [
        (
            "index",
            "custom_records",
            "12345",
            {
                "id": "12345",
                "title": "Test Title",
                "description": "Test description",
                "record_type": "paper",
                "status": "draft",
                "license": "CC BY 4.0",
                "doi": "10.1234/test",
                "publication_date": None,
                "created_at": None,
                "updated_at": None,
            },
            "wait_for",
        )
    ]


def test_delete_research_record_document_returns_true_when_deleted():
    client = DummyClient()
    client.indices = type("Indices", (), {})()

    result = delete_research_record_document(client, "12345", config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert result is True
    assert client.calls == [("delete", "custom_records", "12345", "wait_for")]


def test_update_research_record_document_reindexes_existing_document():
    client = DummyClient()
    record = DummyRecord()

    response = update_research_record_document(client, record, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert response["result"] == "created"
    assert client.calls == [
        (
            "index",
            "custom_records",
            "12345",
            {
                "id": "12345",
                "title": "Test Title",
                "description": "Test description",
                "record_type": "paper",
                "status": "draft",
                "license": "CC BY 4.0",
                "doi": "10.1234/test",
                "publication_date": None,
                "created_at": None,
                "updated_at": None,
            },
            "wait_for",
        )
    ]


def test_delete_research_record_document_returns_false_when_missing():
    client = DummyMissingClient()
    client.indices = type("Indices", (), {})()

    result = delete_research_record_document(client, "12345", config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert result is False
    assert client.calls == [("delete", "custom_records", "12345", "wait_for")]


def test_rebuild_records_index_deletes_and_recreates_index(monkeypatch):
    client = DummyClient()
    client.indices = type(
        "Indices",
        (),
        {
            "exists": lambda self, index: True,
            "delete": lambda self, index: client.calls.append(("delete_index", index)),
            "create": lambda self, index, body: client.calls.append(("create", index, body)),
        },
    )()

    monkeypatch.setattr("app.search.services.get_opensearch_client", lambda: client)

    results = rebuild_records_index([],)

    assert results == {"indexed": 0, "failed": 0}
    assert client.calls == [("delete_index", "research_records"), ("create", "research_records", INDEX_BODY)]


def test_rebuild_records_index_indexes_all_successful_records(monkeypatch):
    client = DummyClient()
    client.indices = type(
        "Indices",
        (),
        {
            "exists": lambda self, index: False,
            "delete": lambda self, index: client.calls.append(("delete_index", index)),
            "create": lambda self, index, body: client.calls.append(("create", index, body)),
        },
    )()

    record1 = DummyRecord()
    record2 = DummyRecord()
    record2.id = "67890"
    record2.title = "Other Title"

    monkeypatch.setattr("app.search.services.get_opensearch_client", lambda: client)

    results = rebuild_records_index([record1, record2])

    assert results == {"indexed": 2, "failed": 0}
    assert client.calls[0] == ("create", "research_records", INDEX_BODY)
    assert client.calls[1][0] == "index"
    assert client.calls[2][0] == "index"


def test_rebuild_records_index_counts_failures_and_continues(monkeypatch):
    class FailingIndexClient(DummyClient):
        def index(self, *, index, id, body, refresh):
            super().index(index=index, id=id, body=body, refresh=refresh)
            if id == "bad-id":
                raise RuntimeError("index failure")
            return {"result": "created", "_id": id}

    client = FailingIndexClient()
    client.indices = type(
        "Indices",
        (),
        {
            "exists": lambda self, index: False,
            "delete": lambda self, index: client.calls.append(("delete_index", index)),
            "create": lambda self, index, body: client.calls.append(("create", index, body)),
        },
    )()

    good_record = DummyRecord()
    bad_record = DummyRecord()
    bad_record.id = "bad-id"

    monkeypatch.setattr("app.search.services.get_opensearch_client", lambda: client)

    results = rebuild_records_index([good_record, bad_record])

    assert results == {"indexed": 1, "failed": 1}
    assert client.calls[0] == ("create", "research_records", INDEX_BODY)
    assert client.calls[1][0] == "index"
    assert client.calls[2][0] == "index"


def test_custom_configured_index_name_is_used_for_all_operations():
    client = DummyClient()
    state = {"created": False}

    def exists(self, index):
        return state["created"]

    def create(index, body):
        state["created"] = True
        client.calls.append(("create", index, body))

    client.indices = type(
        "Indices",
        (),
        {
            "exists": exists,
            "create": lambda self, index, body: create(index, body),
            "delete": lambda self, index: client.calls.append(("delete_index", index)),
        },
    )()

    create_records_index(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})
    delete_records_index(client, config={"OPENSEARCH_RECORDS_INDEX": "custom_records"})

    assert client.calls == [
        ("create", "custom_records", INDEX_BODY),
        ("delete_index", "custom_records"),
    ]
