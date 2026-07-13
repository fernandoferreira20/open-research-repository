"""Routes for PDF upload, download, replacement, and deletion."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request, send_file
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import RequestEntityTooLarge

from .services import (
    ConflictError,
    NotFoundError,
    StoredFileMissingError,
    create_research_file,
    delete_research_file,
    get_research_file_for_download,
    replace_research_file,
)
from .validators import ValidationError, validate_file_upload_request


files_bp = Blueprint("files", __name__, url_prefix="/api/records")


def _error_response(code: str, message: str, details: dict | None = None, status: int = 400):
    payload = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status


@files_bp.app_errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(_error):
    max_size_mb = current_app.config.get("MAX_UPLOAD_SIZE_MB", 10)
    return _error_response(
        "payload_too_large",
        f"File size exceeds the maximum allowed size of {max_size_mb} MB.",
        None,
        413,
    )


@files_bp.route("/<uuid:record_id>/file", methods=["POST"])
def upload_record_file(record_id):
    """Upload a PDF for a research record."""
    try:
        upload_data = validate_file_upload_request(request, current_app.config["MAX_CONTENT_LENGTH"])
    except ValidationError as exc:
        return _error_response("validation_error", "Validation failed.", exc.details, 400)

    try:
        research_file = create_research_file(record_id, upload_data)
        return jsonify({"file": research_file.to_dict()}), 201
    except NotFoundError as exc:
        return _error_response("not_found", str(exc), None, 404)
    except ConflictError as exc:
        return _error_response("conflict", str(exc), None, 409)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error.", None, 500)
    except Exception:
        return _error_response("server_error", "Unexpected error.", None, 500)


@files_bp.route("/<uuid:record_id>/file", methods=["GET"])
def download_record_file(record_id):
    """Download the PDF attached to a research record."""
    try:
        research_file, file_path = get_research_file_for_download(record_id)
        return send_file(
            file_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=research_file.original_filename,
        )
    except NotFoundError as exc:
        return _error_response("not_found", str(exc), None, 404)
    except StoredFileMissingError as exc:
        return _error_response("not_found", str(exc), None, 404)
    except Exception:
        return _error_response("server_error", "Unexpected error.", None, 500)


@files_bp.route("/<uuid:record_id>/file", methods=["PUT"])
def replace_record_file(record_id):
    """Replace the PDF attached to a research record."""
    try:
        upload_data = validate_file_upload_request(request, current_app.config["MAX_CONTENT_LENGTH"])
    except ValidationError as exc:
        return _error_response("validation_error", "Validation failed.", exc.details, 400)

    try:
        research_file = replace_research_file(record_id, upload_data)
        return jsonify({"file": research_file.to_dict()}), 200
    except NotFoundError as exc:
        return _error_response("not_found", str(exc), None, 404)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error.", None, 500)
    except Exception:
        return _error_response("server_error", "Unexpected error.", None, 500)


@files_bp.route("/<uuid:record_id>/file", methods=["DELETE"])
def delete_record_file_route(record_id):
    """Delete the PDF attached to a research record."""
    try:
        delete_research_file(record_id)
        return "", 204
    except NotFoundError as exc:
        return _error_response("not_found", str(exc), None, 404)
    except SQLAlchemyError:
        return _error_response("server_error", "Database error.", None, 500)
    except Exception:
        return _error_response("server_error", "Unexpected error.", None, 500)
