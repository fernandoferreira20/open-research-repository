"""Search-related HTTP routes for the Flask application."""

from __future__ import annotations

from flask import Blueprint, jsonify, current_app, request
from opensearchpy.exceptions import OpenSearchException

from . import client
from .services import search_research_records
from .validators import ValidationError, validate_search_query_params

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/health", methods=["GET"])
def search_health():
    """Health check endpoint for the OpenSearch service."""
    try:
        opensearch_client = client.get_opensearch_client()
        healthy = opensearch_client.ping()
    except OpenSearchException:
        current_app.logger.exception("OpenSearch health check failed")
        return jsonify({"status": "unavailable", "service": "opensearch"}), 503
    except RuntimeError:
        return jsonify({"status": "unavailable", "service": "opensearch"}), 503

    if healthy:
        return jsonify({"status": "ok", "service": "opensearch"}), 200

    current_app.logger.warning("OpenSearch ping returned false")
    return jsonify({"status": "unavailable", "service": "opensearch"}), 503


@search_bp.route("/records", methods=["GET"])
def search_records():
    """Search research records using OpenSearch full-text search."""
    try:
        options = validate_search_query_params(request.args)
    except ValidationError as exc:
        return (
            jsonify(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Validation failed.",
                        "details": exc.details,
                    }
                }
            ),
            400,
        )

    try:
        results = search_research_records(options)
        return jsonify(results), 200
    except OpenSearchException:
        current_app.logger.exception("OpenSearch search failed")
        return (
            jsonify(
                {
                    "error": {
                        "code": "search_unavailable",
                        "message": "Search service is currently unavailable.",
                    }
                }
            ),
            503,
        )
    except RuntimeError:
        current_app.logger.exception("OpenSearch client is not initialized")
        return (
            jsonify(
                {
                    "error": {
                        "code": "search_unavailable",
                        "message": "Search service is currently unavailable.",
                    }
                }
            ),
            503,
        )
    except Exception:
        current_app.logger.exception("Unexpected search error")
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An internal server error occurred.",
                    }
                }
            ),
            500,
        )
