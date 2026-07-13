"""OpenSearch integration package for the Flask application.

This package contains a centralized client and API routes for search-related
features. It is intentionally kept separate from the main application logic so
search support can grow without affecting core models or routes.
"""

from .client import get_opensearch_client, init_opensearch
from .routes import search_bp

__all__ = ["get_opensearch_client", "init_opensearch", "search_bp"]
