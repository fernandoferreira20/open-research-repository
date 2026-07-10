import os

from flask import Flask

from .config import Config
from .routes import api_bp


def create_app():
    """Create and configure the Flask application.

    The Application Factory pattern allows the app to be created
    with a fresh configuration for each environment or test run.
    It also makes the app easier to extend and scale over time.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register route blueprints here. Blueprints keep route
    # organization modular and make it easy to add new APIs later.
    app.register_blueprint(api_bp)

    return app
