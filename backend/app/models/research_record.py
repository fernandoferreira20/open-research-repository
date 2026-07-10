"""ResearchRecord model.

This file defines the `ResearchRecord` SQLAlchemy model using the modern
2.x typed mapping API (`Mapped`, `mapped_column`). The model represents a
single research item (paper, dataset, software, presentation, etc.).

Do not add business logic, CRUD routes, or migrations here. This is only
the declarative model definition so Flask-Migrate can discover it later.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, date
from typing import Optional

from sqlalchemy import String, Text, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class ResearchRecord(db.Model):
    """A database model representing a research record.

    A database model maps Python objects to database tables. Each instance
    corresponds to a row in the `research_records` table.

    UUIDs are used for the primary key to provide globally unique identifiers
    that are safe to expose in APIs and avoid sequential ID guessing.
    """

    __tablename__ = "research_records"

    # Primary key: UUID generated automatically using uuid.uuid4
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Title of the research record. Indexed for faster lookup by title.
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Longer description stored as TEXT.
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Type of record, e.g., paper, dataset, software, presentation, other.
    # Indexed as queries will often filter by type.
    record_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Status such as draft, published, archived. Defaults to 'draft'.
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    # License string (optional).
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # DOI is optional but should be unique when present.
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)

    # Optional publication date (date without time).
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Timezone-aware UTC timestamps for creation and last update.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of the model.

        - UUIDs are converted to strings.
        - Dates and datetimes are converted to ISO 8601 strings.
        - Optional values are returned as `None` when absent.
        """
        return {
            "id": str(self.id) if self.id is not None else None,
            "title": self.title,
            "description": self.description,
            "record_type": self.record_type,
            "status": self.status,
            "license": self.license,
            "doi": self.doi,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        """Developer-friendly string representation for debugging."""
        return f"<ResearchRecord id={self.id} title={self.title!r}>"
