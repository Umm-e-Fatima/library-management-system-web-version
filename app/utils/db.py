"""
Database utility module.

Provides the SQLAlchemy instance to be used across the application.
This avoids circular dependencies between models and the application factory.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance without attaching to an app yet
db = SQLAlchemy()
