"""Validation helpers for OpenSearch search query parameters."""

from __future__ import annotations

from typing import Any, Dict


class ValidationError(Exception):
    """Raised when search query validation fails."""

    def __init__(self, details: Dict[str, str]):
        super().__init__("Validation failed")
        self.details = details


ALLOWED_RECORD_TYPES = {"paper", "dataset", "software", "presentation", "other"}
ALLOWED_STATUS = {"draft", "published", "archived"}
ALLOWED_SORT_FIELDS = {
    "relevance",
    "created_at",
    "updated_at",
    "publication_date",
    "title",
}
ALLOWED_ORDER = {"asc", "desc"}


def validate_search_query_params(args: Any) -> dict[str, Any]:
    """Validate search query parameters and return normalized options."""
    if not hasattr(args, "keys"):
        raise ValidationError({"_query": "Query parameters must be a mapping"})

    errors: Dict[str, str] = {}
    cleaned: Dict[str, Any] = {}
    known_keys = {"q", "page", "per_page", "status", "record_type", "sort", "order"}

    for key in args.keys():
        if key not in known_keys:
            errors[key] = "Unknown query parameter"

    cleaned["q"] = None
    raw_q = args.get("q")
    if raw_q is not None:
        if not isinstance(raw_q, str):
            errors["q"] = "q must be a string"
        else:
            trimmed = raw_q.strip()
            if len(trimmed) > 200:
                errors["q"] = "q must be at most 200 characters"
            elif trimmed == "":
                cleaned["q"] = None
            else:
                cleaned["q"] = trimmed

    page = args.get("page", "1")
    per_page = args.get("per_page", "10")

    try:
        page_value = int(page)
        if page_value < 1:
            raise ValueError()
        cleaned["page"] = page_value
    except (TypeError, ValueError):
        errors["page"] = "page must be a positive integer"

    try:
        per_page_value = int(per_page)
        if per_page_value < 1 or per_page_value > 100:
            raise ValueError()
        cleaned["per_page"] = per_page_value
    except (TypeError, ValueError):
        errors["per_page"] = "per_page must be a positive integer up to 100"

    status = args.get("status")
    if status is not None:
        if status not in ALLOWED_STATUS:
            errors["status"] = f"status must be one of: {', '.join(sorted(ALLOWED_STATUS))}"
        else:
            cleaned["status"] = status

    record_type = args.get("record_type")
    if record_type is not None:
        if record_type not in ALLOWED_RECORD_TYPES:
            errors["record_type"] = f"record_type must be one of: {', '.join(sorted(ALLOWED_RECORD_TYPES))}"
        else:
            cleaned["record_type"] = record_type

    sort = args.get("sort")
    if sort is None:
        cleaned["sort"] = "relevance" if cleaned["q"] else "created_at"
    elif sort not in ALLOWED_SORT_FIELDS:
        errors["sort"] = f"sort must be one of: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
    else:
        cleaned["sort"] = sort

    order = args.get("order", "desc")
    if order not in ALLOWED_ORDER:
        errors["order"] = "order must be one of: asc, desc"
    else:
        cleaned["order"] = order

    if errors:
        raise ValidationError(errors)

    return cleaned
