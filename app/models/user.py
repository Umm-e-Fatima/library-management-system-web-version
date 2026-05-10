"""
User Model for Library Management System.
Defines the schema for the users table using SQLAlchemy.
"""
from datetime import datetime
from app.utils.db import db

class User(db.Model):
    """
    User model representing individuals with access to the system.
    
    Fields:
        id (int): Primary key for the user.
        username (str): Unique identifier for logging in.
        password (str): Hashed password for security.
        role (str): Permissions level (e.g., 'admin', 'librarian', 'member').
        created_at (datetime): Timestamp of user creation.
    """
    __tablename__ = 'users'

    # Primary key
    id = db.Column(db.Integer, primary key=True, autoincrement=True)
    
    # User Identification
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # Authorization and Metadata
    role = db.Column(db.String(50), nullable=False, default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the User object.
        """
        return f"<User(username='{self.username}', role='{self.role}')>"
