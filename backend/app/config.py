import os


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


class TestConfig(Config):
    """Configuration used only for automated tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = "testing"
