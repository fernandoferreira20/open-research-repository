"""Validation helpers for research record file uploads."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class ValidationError(Exception):
    """Raised when multipart upload validation fails."""

    def __init__(self, details: dict[str, str]):
        super().__init__("Validation failed")
        self.details = details


ALLOWED_EXTENSION = ".pdf"
ALLOWED_MIME_TYPE = "application/pdf"
PDF_SIGNATURE = b"%PDF-"


def _get_file_size(file_storage: FileStorage) -> int:
    stream = file_storage.stream
    current_position = stream.tell()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(current_position)
    return size


def _has_pdf_signature(file_storage: FileStorage) -> bool:
    stream = file_storage.stream
    current_position = stream.tell()
    stream.seek(0)
    header = stream.read(len(PDF_SIGNATURE))
    stream.seek(current_position)
    return header.startswith(PDF_SIGNATURE)


def validate_file_upload_request(request: Any, max_content_length: int) -> dict[str, Any]:
    """Validate a multipart/form-data upload request and normalize file metadata."""
    if getattr(request, "mimetype", None) != "multipart/form-data":
        raise ValidationError({"content_type": "Request must use multipart/form-data"})

    if "file" not in request.files:
        raise ValidationError({"file": "The file field is required"})

    uploaded_file = request.files["file"]
    if not isinstance(uploaded_file, FileStorage):
        raise ValidationError({"file": "The uploaded file is invalid"})

    raw_filename = uploaded_file.filename or ""
    if raw_filename.strip() == "":
        raise ValidationError({"file": "Filename must not be empty"})

    original_filename = secure_filename(raw_filename)
    if original_filename == "":
        raise ValidationError({"file": "Filename must contain safe characters"})

    errors: dict[str, str] = {}

    if len(original_filename) > 255:
        errors["file"] = "Filename must be at most 255 characters"

    extension = Path(original_filename).suffix.lower()
    if extension != ALLOWED_EXTENSION:
        errors["file"] = "Only PDF files are allowed"

    mime_type = (uploaded_file.mimetype or "").lower()
    if mime_type != ALLOWED_MIME_TYPE:
        errors["file"] = "File must have MIME type application/pdf"

    file_size = _get_file_size(uploaded_file)
    if file_size <= 0:
        errors["file"] = "File must not be empty"
    elif file_size > max_content_length:
        errors["file"] = f"File size must not exceed {max_content_length} bytes"

    if not _has_pdf_signature(uploaded_file):
        errors["file"] = "Uploaded file content is not a valid PDF"

    uploaded_file.stream.seek(0)

    if errors:
        raise ValidationError(errors)

    return {
        "file_storage": uploaded_file,
        "original_filename": original_filename,
        "mime_type": ALLOWED_MIME_TYPE,
        "file_size": file_size,
    }
