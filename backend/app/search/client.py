"""Centralized OpenSearch client integration.

A centralized client is used so the application has a single place to manage
connection configuration, initialization, and lifecycle. This avoids creating
network connections during module import and makes the client easy to mock in
tests.
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

from flask import Flask, current_app, has_app_context
from opensearchpy import OpenSearch


def _parse_opensearch_url(raw_url: str) -> tuple[str, int, str]:
    """Parse OPENSEARCH_URL safely into host, port, and scheme."""
    parsed = urlparse(raw_url)
    if not parsed.scheme or not parsed.hostname:
        raise ValueError("OPENSEARCH_URL must be a valid URL")

    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    scheme = parsed.scheme
    return host, port, scheme


def init_opensearch(app: Flask) -> None:
    """Initialize the OpenSearch client and store it on the Flask app extensions.

    The client is stored under `app.extensions['opensearch']` so it can be
    accessed from any request context after initialization without creating
    new connections at import time.
    """
    raw_url = app.config.get("OPENSEARCH_URL") or os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    host, port, scheme = _parse_opensearch_url(raw_url)

    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        scheme=scheme,
        verify_certs=False,
    )

    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["opensearch"] = client


def get_opensearch_client() -> OpenSearch:
    """Return the initialized OpenSearch client from the current app context.

    Raising a RuntimeError here makes it clear to developers when the client
    has not been configured yet or when there is no active application context.
    """
    if not has_app_context():
        raise RuntimeError("OpenSearch client requires an active Flask application context")

    client = current_app.extensions.get("opensearch") if hasattr(current_app, "extensions") else None
    if client is None:
        raise RuntimeError("OpenSearch client has not been initialized. Call init_opensearch(app) first.")
    return client
