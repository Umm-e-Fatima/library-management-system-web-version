"""
Member Model for Library Management System.
Defines the schema for the members table using SQLAlchemy.
"""
from datetime import datetime
from app.utils.db import db

class Member(db.Model):
    """
    Member model representing library subscribers.
    
    Fields:
        id (int): Primary key for the member.
        full_name (str): Full name of the member.
        email (str): Unique email address of the member for communication and identification.
        phone (str): Contact phone number of the member.
        address (str): Residential or mailing address.
        membership_date (datetime): The date when the member joined the library.
    """
    __tablename__ = 'members'

    # Primary key
    id = db.Column(db.Integer, primary key=True, autoincrement=True)
    
    # Personal and Contact Information
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
    # Registration Metadata
    membership_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Member instance.
        """
        return f"<Member(name='{self.full_name}', email='{self.email}')>"
