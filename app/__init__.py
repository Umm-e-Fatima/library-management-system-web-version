"""
Application factory module.

Initializes the Flask application, loads configurations, and configures 
extensions such as SQLAlchemy for SQL Server connectivity.
"""
from flask import Flask
from app.utils.db import db

def create_app(config_class=None):
    """
    Application factory function that creates and configures the Flask app.
    
    Args:
        config_class (object): The configuration object to load settings from.
                               If None, it tries to load from config.py.
                               
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        # Default to loading from config.py if no class is provided
        try:
            from config import Config
            app.config.from_object(Config)
        except ImportError:
            # Fallback configuration for SQL Server if config.py is unavailable
            # Example PyODBC connection string format:
            # mssql+pyodbc://<username>:<password>@<server>/<database>?driver=ODBC+Driver+17+for+SQL+Server
            app.config['SQLALCHEMY_DATABASE_URI'] = (
                "mssql+pyodbc://sa:YourPassword@localhost/LibraryDB?"
                "driver=ODBC+Driver+17+for+SQL+Server"
            )
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app instance
    db.init_app(app)
    
    with app.app_context():
        # Import models here so SQLAlchemy knows about them before creating tables
        # from app.models import ...
        
        # Register blueprints (routes) here to avoid circular imports
        # Example:
        # from app.routes.book_routes import book_bp
        # app.register_blueprint(book_bp, url_prefix='/books')
        pass
        
    return app
