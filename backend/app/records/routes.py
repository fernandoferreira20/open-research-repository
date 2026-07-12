"""HTTP routes for research records.

Routes are intentionally thin: they parse the HTTP request, delegate to
validators and services, and translate results into HTTP responses.
"""
from __future__ import annotations

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from .validators import validate_create_payload, validate_update_payload, ValidationError
from .services import (
    create_research_record,
    list_research_records,
    get_research_record,
    update_research_record,
    delete_research_record,
    NotFoundError,
    DuplicateDOIError,
)

records_bp = Blueprint("records", __name__, url_prefix="/api/records")


def _error_response(code: str, message: str, details: dict | None = None, status: int = 400):
    payload = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status


@records_bp.route("", methods=["POST"])
def create_record():
    """Create a new research record.

    Flow: parse JSON -> validate -> call service -> return created object.
    """
    try:
        payload = request.get_json(force=True)
    except Exception:
        return _error_response("validation_error", "Validation failed.", {"_payload": "Invalid JSON"}, 400)

    try:
        data = validate_create_payload(payload)
    except ValidationError as exc:
        return _error_response("validation_error", "Validation failed.", exc.details, 400)

    try:
        record = create_research_record(data)
        return jsonify(record.to_dict()), 201
    except DuplicateDOIError as exc:
        return _error_response("conflict", "Duplicate DOI.", {"doi": str(exc)}, 409)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error." , None, 500)
    except Exception:
        return _error_response("server_error", "Unexpected error." , None, 500)


@records_bp.route("", methods=["GET"])
def list_records():
    """List all research records ordered by `created_at` desc."""
    try:
        records = list_research_records()
        return jsonify([r.to_dict() for r in records]), 200
    except SQLAlchemyError:
        return _error_response("server_error", "Database error." , None, 500)


@records_bp.route("/<uuid:record_id>", methods=["GET"])
def get_record(record_id):
    """Retrieve a single record by UUID."""
    try:
        record = get_research_record(record_id)
        return jsonify(record.to_dict()), 200
    except NotFoundError:
        return _error_response("not_found", "Record not found.", None, 404)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error." , None, 500)


@records_bp.route("/<uuid:record_id>", methods=["PUT"])
def update_record(record_id):
    """Update an existing research record."""
    try:
        payload = request.get_json(force=True)
    except Exception:
        return _error_response("validation_error", "Validation failed.", {"_payload": "Invalid JSON"}, 400)

    try:
        data = validate_update_payload(payload)
    except ValidationError as exc:
        return _error_response("validation_error", "Validation failed.", exc.details, 400)

    try:
        record = update_research_record(record_id, data)
        return jsonify(record.to_dict()), 200
    except NotFoundError:
        return _error_response("not_found", "Record not found.", None, 404)
    except DuplicateDOIError as exc:
        return _error_response("conflict", "Duplicate DOI.", {"doi": str(exc)}, 409)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error." , None, 500)
    except Exception:
        return _error_response("server_error", "Unexpected error." , None, 500)


@records_bp.route("/<uuid:record_id>", methods=["DELETE"])
def delete_record(record_id):
    """Delete a research record by UUID."""
    try:
        delete_research_record(record_id)
        return "", 204
    except NotFoundError:
        return _error_response("not_found", "Record not found.", None, 404)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error." , None, 500)
    except Exception:
        return _error_response("server_error", "Unexpected error." , None, 500)
