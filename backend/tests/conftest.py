"""Pytest fixtures for backend tests.

Fixtures provide shared objects to test functions. They help keep tests
isolated and reusable while ensuring the application uses an in-memory
SQLite database rather than the development PostgreSQL database.
"""
import shutil

import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing."""
    app = create_app(TestConfig)
    yield app


@pytest.fixture(scope="session")
def client(app):
    """Flask test client for sending HTTP requests to the app."""
    return app.test_client()


@pytest.fixture(autouse=True)
def database(app):
    """Create and drop database tables around each test session.

    Using an in-memory SQLite database keeps tests isolated from PostgreSQL
    development data. The schema is created once per session here.
    """
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture(autouse=True)
def upload_folder(app, tmp_path):
    """Give each test an isolated upload folder."""
    upload_dir = tmp_path / "uploads" / "records"
    app.config["UPLOAD_FOLDER"] = str(upload_dir)
    app.config["MAX_UPLOAD_SIZE_MB"] = 10
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    yield upload_dir
    shutil.rmtree(upload_dir.parent.parent, ignore_errors=True)
