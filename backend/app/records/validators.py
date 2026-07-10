"""Validation helpers for records endpoints.

Keep validation logic separate from route handlers so it can be tested
independently and reused by other interfaces (CLI, background jobs, etc.).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple


class ValidationError(Exception):
    """Raised when payload validation fails.

    The `details` attribute contains a mapping of field -> error message.
    """

    def __init__(self, details: Dict[str, str]):
        super().__init__("Validation failed")
        self.details = details


ALLOWED_RECORD_TYPES = {"paper", "dataset", "software", "presentation", "other"}
ALLOWED_STATUS = {"draft", "published", "archived"}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_create_payload(payload: Any) -> Dict[str, Any]:
    """Validate and normalize the payload for creating a ResearchRecord.

    Returns a cleaned dict suitable for service layer consumption or raises
    `ValidationError` with detailed messages.
    """
    if not isinstance(payload, dict):
        raise ValidationError({"_payload": "JSON body must be an object"})

    errors: Dict[str, str] = {}
    cleaned: Dict[str, Any] = {}

    # Title: required, non-empty, max 255
    title = payload.get("title")
    if not _is_non_empty_string(title):
        errors["title"] = "Title is required and must be a non-empty string"
    else:
        title = title.strip()
        if len(title) > 255:
            errors["title"] = "Title must be at most 255 characters"
        else:
            cleaned["title"] = title

    # Description: required, non-empty
    description = payload.get("description")
    if not _is_non_empty_string(description):
        errors["description"] = "Description is required and must be a non-empty string"
    else:
        cleaned["description"] = description.strip()

    # Record type: required, must be one of the allowed set
    record_type = payload.get("record_type")
    if not _is_non_empty_string(record_type):
        errors["record_type"] = "record_type is required and must be a non-empty string"
    else:
        record_type = record_type.strip()
        if record_type not in ALLOWED_RECORD_TYPES:
            errors["record_type"] = f"record_type must be one of: {', '.join(sorted(ALLOWED_RECORD_TYPES))}"
        else:
            cleaned["record_type"] = record_type

    # Status: optional, default to 'draft', must be allowed
    status = payload.get("status")
    if status is None:
        cleaned["status"] = "draft"
    elif not isinstance(status, str):
        errors["status"] = "status must be a string"
    else:
        status = status.strip()
        if status not in ALLOWED_STATUS:
            errors["status"] = f"status must be one of: {', '.join(sorted(ALLOWED_STATUS))}"
        else:
            cleaned["status"] = status

    # License: optional, max length 100
    license_val = payload.get("license")
    if license_val is not None:
        if not isinstance(license_val, str):
            errors["license"] = "license must be a string"
        else:
            license_val = license_val.strip()
            if len(license_val) > 100:
                errors["license"] = "license must be at most 100 characters"
            else:
                cleaned["license"] = license_val

    # DOI: optional, max length 255
    doi = payload.get("doi")
    if doi is not None:
        if not isinstance(doi, str):
            errors["doi"] = "doi must be a string"
        else:
            doi = doi.strip()
            if len(doi) > 255:
                errors["doi"] = "doi must be at most 255 characters"
            else:
                cleaned["doi"] = doi

    # publication_date: optional, must be YYYY-MM-DD
    pub_date = payload.get("publication_date")
    if pub_date is not None:
        if not isinstance(pub_date, str):
            errors["publication_date"] = "publication_date must be an ISO date string YYYY-MM-DD"
        else:
            try:
                dt = datetime.strptime(pub_date.strip(), "%Y-%m-%d").date()
                cleaned["publication_date"] = dt
            except ValueError:
                errors["publication_date"] = "publication_date must be in format YYYY-MM-DD"

    if errors:
        raise ValidationError(errors)

    return cleaned
