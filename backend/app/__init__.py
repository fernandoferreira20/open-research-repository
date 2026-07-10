from flask import Flask

from .config import Config
from .extensions import db, migrate
from .routes import api_bp


def create_app():
    """Create and configure the Flask application.

    The Application Factory pattern allows the app to be created
    with a fresh configuration for each environment or test run.
    It also makes the app easier to extend and scale over time.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extension objects with the Flask app instance.
    # This binds SQLAlchemy and migration support to the app.
    db.init_app(app)
    migrate.init_app(app, db)

    # Register route blueprints here. Blueprints keep route
    # organization modular and make it easy to add new APIs later.
    app.register_blueprint(api_bp)

    return app
