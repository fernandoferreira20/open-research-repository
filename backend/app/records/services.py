"""Service layer for research records.

The service layer contains business logic and database interactions. It
is intentionally decoupled from Flask request objects to keep it testable
and reusable in other contexts (CLI, tasks, etc.).
"""
from __future__ import annotations

from typing import List
import uuid

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import ResearchRecord
from app.files.services import remove_file_from_disk
from app.search.client import get_opensearch_client
from app.search.services import (
    delete_research_record_document,
    index_research_record,
    update_research_record_document,
)


class NotFoundError(Exception):
    pass


class DuplicateDOIError(Exception):
    pass


def create_research_record(data: dict) -> ResearchRecord:
    """Create a ResearchRecord and persist it to the database.

    The function commits the transaction or rolls it back on error. It
    raises `DuplicateDOIError` when a unique DOI constraint is violated.
    """
    record = ResearchRecord(
        title=data["title"],
        description=data["description"],
        record_type=data["record_type"],
        status=data.get("status", "draft"),
        license=data.get("license"),
        doi=data.get("doi"),
        publication_date=data.get("publication_date"),
    )

    try:
        db.session.add(record)
        db.session.commit()
        # Refresh to get any DB-side defaults
        db.session.refresh(record)
        try:
            index_research_record(get_opensearch_client(), record, config=current_app.config)
        except Exception:
            current_app.logger.exception(
                "OpenSearch indexing failed during create for record id=%s",
                record.id,
            )
        return record
    except IntegrityError as exc:
        db.session.rollback()
        # Detect unique constraint on doi; databases may name constraints
        # differently, so a simple heuristic is used.
        if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
            raise DuplicateDOIError("A record with this DOI already exists")
        raise
    except Exception:
        db.session.rollback()
        raise


def list_research_records(options: dict | None = None) -> dict:
    """Return paginated ResearchRecord objects using the supplied query options.

    The query is built incrementally to apply filters, search, sorting, and
    pagination in the database, which avoids loading all records into memory.
    """
    options = options or {}
    page = options.get("page", 1)
    per_page = options.get("per_page", 10)
    status = options.get("status")
    record_type = options.get("record_type")
    q = options.get("q")
    sort = options.get("sort", "created_at")
    order = options.get("order", "desc")

    query = db.session.query(ResearchRecord)

    if status is not None:
        query = query.filter(ResearchRecord.status == status)

    if record_type is not None:
        query = query.filter(ResearchRecord.record_type == record_type)

    if q is not None and q != "":
        search_term = f"%{q}%"
        query = query.filter(
            ResearchRecord.title.ilike(search_term)
            | ResearchRecord.description.ilike(search_term)
            | ResearchRecord.doi.ilike(search_term)
        )

    sort_columns = {
        "created_at": ResearchRecord.created_at,
        "updated_at": ResearchRecord.updated_at,
        "publication_date": ResearchRecord.publication_date,
        "title": ResearchRecord.title,
    }

    sort_column = sort_columns.get(sort, ResearchRecord.created_at)
    direction = sort_column.asc() if order == "asc" else sort_column.desc()
    query = query.order_by(direction)

    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page if per_page else 1
    items = (
        query.limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def get_research_record(record_id: uuid.UUID) -> ResearchRecord:
    """Retrieve a ResearchRecord by its UUID or raise NotFoundError."""
    record = db.session.get(ResearchRecord, record_id)
    if record is None:
        raise NotFoundError("ResearchRecord not found")
    return record


def update_research_record(record_id: uuid.UUID, data: dict) -> ResearchRecord:
    """Update fields on an existing ResearchRecord.

    Only supplied editable fields are changed. Immutable fields such as
    `id`, `created_at`, and `updated_at` are not modified directly.
    """
    record = get_research_record(record_id)

    for field, value in data.items():
        setattr(record, field, value)

    try:
        db.session.commit()
        db.session.refresh(record)
        try:
            update_research_record_document(get_opensearch_client(), record, config=current_app.config)
        except Exception:
            current_app.logger.exception(
                "OpenSearch indexing failed during update for record id=%s",
                record.id,
            )
        return record
    except IntegrityError as exc:
        db.session.rollback()
        if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
            raise DuplicateDOIError("A record with this DOI already exists")
        raise
    except Exception:
        db.session.rollback()
        raise


def delete_research_record(record_id: uuid.UUID) -> None:
    """Delete a ResearchRecord by UUID."""
    record = get_research_record(record_id)
    record_id_value = record.id
    stored_file_path = record.file.file_path if record.file is not None else None

    try:
        db.session.delete(record)
        db.session.commit()
        if stored_file_path is not None:
            try:
                remove_file_from_disk(stored_file_path)
            except Exception:
                current_app.logger.exception(
                    "Stored file cleanup failed after record deletion for record id=%s",
                    record_id_value,
                )
        try:
            delete_research_record_document(get_opensearch_client(), record_id_value, config=current_app.config)
        except Exception:
            current_app.logger.exception(
                "OpenSearch deletion failed for record id=%s",
                record_id_value,
            )
    except Exception:
        db.session.rollback()
        raise
