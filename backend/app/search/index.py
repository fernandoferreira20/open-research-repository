"""OpenSearch index definitions and document serialization.

This module defines the index name, settings, and mappings for ResearchRecord
documents. Explicit mappings are useful because they tell OpenSearch the exact
field types and avoid dynamic mapping surprises.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

DEFAULT_RECORDS_INDEX = "research_records"

INDEX_BODY = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "description": {"type": "text"},
            "record_type": {"type": "keyword"},
            "status": {"type": "keyword"},
            "license": {"type": "keyword"},
            "doi": {"type": "keyword"},
            "publication_date": {"type": "date"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}


def _serialize_value(value: object) -> object:
    """Convert Python values into JSON-serializable OpenSearch document values."""
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def research_record_to_document(record: object) -> dict[str, object | None]:
    """Serialize a ResearchRecord model into a plain JSON-serializable dict."""
    return {
        "id": _serialize_value(record.id),
        "title": _serialize_value(record.title),
        "description": _serialize_value(record.description),
        "record_type": _serialize_value(record.record_type),
        "status": _serialize_value(record.status),
        "license": _serialize_value(record.license),
        "doi": _serialize_value(record.doi),
        "publication_date": _serialize_value(record.publication_date),
        "created_at": _serialize_value(record.created_at),
        "updated_at": _serialize_value(record.updated_at),
    }
