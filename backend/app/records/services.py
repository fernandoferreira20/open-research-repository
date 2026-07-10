"""Service layer for research records.

The service layer contains business logic and database interactions. It
is intentionally decoupled from Flask request objects to keep it testable
and reusable in other contexts (CLI, tasks, etc.).
"""
from __future__ import annotations

from typing import List
import uuid

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import ResearchRecord


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


def list_research_records() -> List[ResearchRecord]:
    """Return all ResearchRecord objects ordered by newest first."""
    return (
        db.session.query(ResearchRecord)
        .order_by(ResearchRecord.created_at.desc())
        .all()
    )


def get_research_record(record_id: uuid.UUID) -> ResearchRecord:
    """Retrieve a ResearchRecord by its UUID or raise NotFoundError."""
    record = db.session.get(ResearchRecord, record_id)
    if record is None:
        raise NotFoundError("ResearchRecord not found")
    return record
