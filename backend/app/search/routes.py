"""Search-related HTTP routes for the Flask application."""

from __future__ import annotations

from flask import Blueprint, jsonify, current_app
from opensearchpy import OpenSearch
from opensearchpy.exceptions import OpenSearchException

from . import client

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/health", methods=["GET"])
def search_health():
    """Health check endpoint for the OpenSearch service."""
    try:
        opensearch_client = client.get_opensearch_client()
        healthy = opensearch_client.ping()
    except OpenSearchException as exc:
        current_app.logger.exception("OpenSearch health check failed")
        return jsonify({"status": "unavailable", "service": "opensearch"}), 503
    except RuntimeError:
        return jsonify({"status": "unavailable", "service": "opensearch"}), 503

    if healthy:
        return jsonify({"status": "ok", "service": "opensearch"}), 200

    current_app.logger.warning("OpenSearch ping returned false")
    return jsonify({"status": "unavailable", "service": "opensearch"}), 503
