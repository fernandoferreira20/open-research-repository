"""ResearchFile model for storing uploaded PDF metadata."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class ResearchFile(db.Model):
    """Metadata for a PDF attached to a research record."""

    __tablename__ = "research_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_records.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    record: Mapped["ResearchRecord"] = relationship(back_populates="file")

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of the model."""
        record_id = str(self.record_id) if self.record_id is not None else None
        return {
            "id": str(self.id) if self.id is not None else None,
            "record_id": record_id,
            "original_filename": self.original_filename,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "download_url": f"/api/records/{record_id}/file" if record_id else None,
        }

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<ResearchFile id={self.id} record_id={self.record_id}>"
