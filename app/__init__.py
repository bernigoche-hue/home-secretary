from flask import Flask

from app.extensions import db, login_manager


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."

    # Import models so SQLAlchemy knows about them
    from app import models

    # Register routes
    from app.routes import main
    app.register_blueprint(main)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app