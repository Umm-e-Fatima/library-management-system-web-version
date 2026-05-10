"""
Book Model for Library Management System.
Defines the schema for the books table using SQLAlchemy.
"""
from datetime import datetime
from app.utils.db import db

class Book(db.Model):
    """
    Book model representing a library resource.
    
    Fields:
        id (int): Primary key for the book.
        title (str): Title of the book.
        author (str): Author of the book.
        category (str): Genre or category of the book.
        quantity (int): Total number of copies owned by the library.
        available_quantity (int): Number of copies currently available for borrowing.
        published_year (int): The year the book was published.
        created_at (datetime): Timestamp of when the book record was created.
    """
    __tablename__ = 'books'

    # Primary key
    id = db.Column(db.Integer, primary key=True, autoincrement=True)
    
    # Core Book Information
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    
    # Inventory and Stock Tracking
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Publication and Record Metadata
    published_year = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Book object for debugging and logging.
        """
        return f"<Book(title='{self.title}', author='{self.author}', available={self.available_quantity})>"
