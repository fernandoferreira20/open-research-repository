"""OpenSearch indexing service for ResearchRecord documents."""

from __future__ import annotations

import logging
from typing import Any, Iterable

from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError

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


def rebuild_records_index(
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
