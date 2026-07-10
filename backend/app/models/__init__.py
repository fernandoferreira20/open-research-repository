"""Models package.

Import models here so they are available when the application starts.
Flask-Migrate (Alembic) detects models by importing modules that define
`db.Model` subclasses before generating migrations.

Avoid importing application-level objects here to prevent circular imports.
This module simply imports model classes to make them visible.
"""

# Import model classes so Flask-Migrate can discover them when the app
# package is imported during `create_app()` execution.
from .research_record import ResearchRecord

__all__ = ["ResearchRecord"]
