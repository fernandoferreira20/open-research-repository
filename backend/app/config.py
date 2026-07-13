import os
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CONTAINER_UPLOAD_FOLDER = Path("/app/uploads/records")
LOCAL_UPLOAD_FOLDER = BASE_DIR / "uploads" / "records"


def _get_upload_folder() -> str:
    configured_upload_folder = os.getenv("UPLOAD_FOLDER")
    if configured_upload_folder:
        return configured_upload_folder

    flask_env = os.getenv("FLASK_ENV", "production")
    if flask_env == "development" and not Path("/app").exists():
        return str(LOCAL_UPLOAD_FOLDER)

    return str(CONTAINER_UPLOAD_FOLDER)


def _get_max_upload_size_mb() -> int:
    value = os.getenv("MAX_UPLOAD_SIZE_MB", "10")
    try:
        parsed = int(value)
    except ValueError:
        parsed = 10
    return max(parsed, 1)


class Config:
    """Application configuration loaded from environment variables."""

    # Secret key used for session signing and CSRF protection.
    SECRET_KEY = os.getenv("SECRET_KEY", "please-set-a-secret-key")

    # Database connection string for SQLAlchemy.
    # This is the standard place to define the database URI for Flask apps.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")

    # Disable the event system that tracks object modifications.
    # It is not needed in most apps and saves memory.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask environment mode: development, production, or testing.
    FLASK_ENV = os.getenv("FLASK_ENV", "production")

    # Filesystem directory where uploaded PDFs are stored.
    UPLOAD_FOLDER = _get_upload_folder()

    # Maximum upload size in megabytes and bytes.
    MAX_UPLOAD_SIZE_MB = _get_max_upload_size_mb()
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # OpenSearch connection URL used by the centralized client.
    OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://localhost:9200")

    # OpenSearch index name for ResearchRecord documents.
    OPENSEARCH_RECORDS_INDEX = os.getenv("OPENSEARCH_RECORDS_INDEX", "research_records")


class TestConfig(Config):
    """Configuration used only for automated tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = "testing"
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "open-research-repository-test-uploads")
    MAX_UPLOAD_SIZE_MB = 10
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
