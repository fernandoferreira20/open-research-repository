"""Central place to initialize Flask extensions.

Extensions are created at import time so they can be declared globally and
then initialized with a specific Flask app instance inside `create_app()`.
This supports the Application Factory pattern and keeps the app extensible.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create extension objects outside of create_app() so they can be imported
# by other modules without requiring an application instance.
# The actual Flask app is bound later using `init_app()`.
db = SQLAlchemy()
migrate = Migrate()
