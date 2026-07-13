"""OpenSearch indexing service for ResearchRecord documents."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError

from . import client
from .client import get_opensearch_client
from .index import DEFAULT_RECORDS_INDEX, INDEX_BODY, research_record_to_document

logger = logging.getLogger(__name__)


def _resolve_records_index_name(config: dict[str, Any] | None = None, index_name: str | None = None) -> str:
    """Resolve the OpenSearch index name using config or a fallback."""
    if index_name:
        return index_name
    if config is not None:
        return str(config.get("OPENSEARCH_RECORDS_INDEX") or DEFAULT_RECORDS_INDEX)
    return DEFAULT_RECORDS_INDEX


def index_exists(
    client: OpenSearch,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Return whether the records index exists in OpenSearch."""
    index = _resolve_records_index_name(config, index_name)
    return bool(client.indices.exists(index=index))


def create_records_index(
    client: OpenSearch,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Create the records index only when it does not already exist."""
    index = _resolve_records_index_name(config, index_name)
    if client.indices.exists(index=index):
        return False

    client.indices.create(index=index, body=INDEX_BODY)
    return True


def delete_records_index(
    client: OpenSearch,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Delete the records index only when it is present."""
    index = _resolve_records_index_name(config, index_name)
    if not client.indices.exists(index=index):
        return False

    client.indices.delete(index=index)
    return True


def ensure_records_index(
    client: OpenSearch,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Create the records index if it does not already exist.

    Returns True when the index was created and False when it already existed.
    """
    return create_records_index(client, index_name=index_name, config=config)


def index_research_record(
    client: OpenSearch,
    record: object,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, object]:
    """Index a ResearchRecord document in OpenSearch."""
    index = _resolve_records_index_name(config, index_name)
    document = research_record_to_document(record)

    return client.index(
        index=index,
        id=document["id"],
        body=document,
        refresh="wait_for",
    )


def update_research_record_document(
    client: OpenSearch,
    record: object,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, object]:
    """Replace or update the ResearchRecord document using its database UUID."""
    index = _resolve_records_index_name(config, index_name)
    document = research_record_to_document(record)

    return client.index(
        index=index,
        id=document["id"],
        body=document,
        refresh="wait_for",
    )


def delete_research_record_document(
    client: OpenSearch,
    record_id: object,
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """Delete a ResearchRecord document from OpenSearch by id."""
    index = _resolve_records_index_name(config, index_name)
    try:
        response = client.delete(index=index, id=str(record_id), refresh="wait_for")
        return response.get("result") == "deleted"
    except NotFoundError:
        return False


def _rebuild_records_index(
    client: OpenSearch,
    records: Iterable[object],
    index_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Rebuild the records index from the supplied ResearchRecord objects."""
    index = _resolve_records_index_name(config, index_name)

    if client.indices.exists(index=index):
        client.indices.delete(index=index)

    client.indices.create(index=index, body=INDEX_BODY)

    indexed = 0
    failed = 0
    for record in records:
        try:
            index_research_record(client, record, index_name=index)
            indexed += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to index ResearchRecord with id=%s into OpenSearch index %s",
                getattr(record, "id", "<unknown>"),
                index,
            )

    return {"indexed": indexed, "failed": failed}


def rebuild_records_index(records: Iterable[object]) -> dict[str, int]:
    """Rebuild the records index from the supplied ResearchRecord objects.

    This public API obtains the centralized OpenSearch client internally.
    """
    opensearch_client = get_opensearch_client()
    return _rebuild_records_index(opensearch_client, records)


def search_research_records(options: dict[str, Any]) -> dict[str, Any]:
    """Execute a full-text search against the ResearchRecord OpenSearch index."""
    opensearch_client = client.get_opensearch_client()
    index = _resolve_records_index_name()

    query_body: dict[str, Any] = {"query": {}}
    filters: list[dict[str, Any]] = []

    if options["q"]:
        query_body["query"] = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": options["q"],
                            "fields": ["title^3", "description", "doi^2"],
                            "type": "best_fields",
                            "operator": "and",
                        }
                    }
                ],
                "filter": filters,
            }
        }
    else:
        query_body["query"] = {
            "bool": {
                "must": {"match_all": {}},
                "filter": filters,
            }
        }

    if options.get("status") is not None:
        filters.append({"term": {"status": options["status"]}})

    if options.get("record_type") is not None:
        filters.append({"term": {"record_type": options["record_type"]}})

    sort_field_map = {
        "relevance": None,
        "created_at": {"created_at": {"order": options["order"]}},
        "updated_at": {"updated_at": {"order": options["order"]}},
        "publication_date": {"publication_date": {"order": options["order"]}},
        "title": {"title.keyword": {"order": options["order"]}},
    }

    if options["sort"] != "relevance" or not options["q"]:
        query_body["sort"] = [sort_field_map[options["sort"]]]
    else:
        query_body["sort"] = ["_score"]

    query_body["from"] = (options["page"] - 1) * options["per_page"]
    query_body["size"] = options["per_page"]
    query_body["_source"] = True

    response = opensearch_client.search(index=index, body=query_body)
    hits = response.get("hits", {})
    total = hits.get("total", {})
    total_value = total.get("value", 0)

    items = []
    for hit in hits.get("hits", []):
        source = hit.get("_source", {})
        items.append(
            {**source, "score": hit.get("_score")}
        )

    total_pages = (total_value + options["per_page"] - 1) // options["per_page"] if options["per_page"] else 0

    return {
        "items": items,
        "pagination": {
            "page": options["page"],
            "per_page": options["per_page"],
            "total_items": total_value,
            "total_pages": total_pages,
            "has_next": options["page"] < total_pages,
            "has_previous": options["page"] > 1,
        },
    }
