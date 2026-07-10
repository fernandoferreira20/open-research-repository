"""Central place to initialize Flask extensions.

This module exists so extension instances can be imported from a single
location and initialized in `create_app()` later. Example extensions include
ORMs, migration tools, caching, and authentication helpers.
"""

# Example placeholder for future extension support:
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

# Do not create extensions here yet. Initialize them inside create_app()
# when the backend architecture is expanded.
