"""Service layer for research record file uploads."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import current_app

from app.extensions import db
from app.models import ResearchFile, ResearchRecord


class NotFoundError(Exception):
    """Raised when a record or file cannot be found."""


class ConflictError(Exception):
    """Raised when a record already has a file attached."""


class StoredFileMissingError(Exception):
    """Raised when file metadata exists but the file is missing on disk."""


def _get_record(record_id: uuid.UUID) -> ResearchRecord:
    record = db.session.get(ResearchRecord, record_id)
    if record is None:
        raise NotFoundError("Research record not found")
    return record


def _get_upload_directory() -> Path:
    upload_directory = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    upload_directory.mkdir(parents=True, exist_ok=True)
    return upload_directory


def _build_stored_filename() -> str:
    return f"{uuid.uuid4().hex}.pdf"


def _build_file_path(stored_filename: str) -> Path:
    return _get_upload_directory() / stored_filename


def _save_uploaded_file(upload_data: dict[str, Any], destination: Path) -> None:
    upload_data["file_storage"].stream.seek(0)
    upload_data["file_storage"].save(destination)


def remove_file_from_disk(file_path: str | Path) -> None:
    """Remove a file from disk if it exists."""
    path = Path(file_path)
    if path.exists():
        path.unlink()


def create_research_file(record_id: uuid.UUID, upload_data: dict[str, Any]) -> ResearchFile:
    """Create file metadata and store the uploaded PDF on disk."""
    record = _get_record(record_id)
    if record.file is not None:
        raise ConflictError("A file already exists for this record")

    stored_filename = _build_stored_filename()
    destination = _build_file_path(stored_filename)
    research_file = ResearchFile(
        record_id=record.id,
        original_filename=upload_data["original_filename"],
        stored_filename=stored_filename,
        mime_type=upload_data["mime_type"],
        file_size=upload_data["file_size"],
        file_path=str(destination),
        uploaded_at=datetime.now(timezone.utc),
    )

    try:
        _save_uploaded_file(upload_data, destination)
        db.session.add(research_file)
        db.session.commit()
        db.session.refresh(research_file)
        return research_file
    except Exception:
        db.session.rollback()
        remove_file_from_disk(destination)
        raise


def get_research_file_for_download(record_id: uuid.UUID) -> tuple[ResearchFile, Path]:
    """Return metadata and physical file path for an existing upload."""
    record = _get_record(record_id)
    if record.file is None:
        raise NotFoundError("Research file not found")

    file_path = Path(record.file.file_path)
    if not file_path.exists():
        raise StoredFileMissingError("Stored file is missing on disk")

    return record.file, file_path


def replace_research_file(record_id: uuid.UUID, upload_data: dict[str, Any]) -> ResearchFile:
    """Replace an existing file while preserving the old file until commit succeeds."""
    record = _get_record(record_id)
    if record.file is None:
        raise NotFoundError("Research file not found")

    research_file = record.file
    old_file_path = Path(research_file.file_path)
    stored_filename = _build_stored_filename()
    new_file_path = _build_file_path(stored_filename)

    try:
        _save_uploaded_file(upload_data, new_file_path)
        research_file.original_filename = upload_data["original_filename"]
        research_file.stored_filename = stored_filename
        research_file.mime_type = upload_data["mime_type"]
        research_file.file_size = upload_data["file_size"]
        research_file.file_path = str(new_file_path)
        research_file.uploaded_at = datetime.now(timezone.utc)

        db.session.commit()
        db.session.refresh(research_file)
    except Exception:
        db.session.rollback()
        remove_file_from_disk(new_file_path)
        raise

    try:
        remove_file_from_disk(old_file_path)
    except Exception:  # pragma: no cover - best-effort cleanup
        current_app.logger.exception(
            "Old file cleanup failed after replacement for record id=%s",
            record.id,
        )

    return research_file


def delete_research_file(record_id: uuid.UUID) -> None:
    """Delete file metadata and remove the PDF from disk."""
    record = _get_record(record_id)
    if record.file is None:
        raise NotFoundError("Research file not found")

    file_path = record.file.file_path

    try:
        db.session.delete(record.file)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    try:
        remove_file_from_disk(file_path)
    except Exception:  # pragma: no cover - best-effort cleanup
        current_app.logger.exception(
            "Stored file cleanup failed after delete for record id=%s",
            record.id,
        )
