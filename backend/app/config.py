import os


class Config:
    """Application configuration loaded from environment variables."""

    # Secret key used by Flask and extensions for session security.
    SECRET_KEY = os.getenv("SECRET_KEY", "please-set-a-secret-key")

    # Database connection string; defined here so the app can be configured
    # from environment variables without hard-coding secrets.
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Flask environment mode: development, production, or testing.
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
