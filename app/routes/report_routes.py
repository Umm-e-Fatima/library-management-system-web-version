"""
Report Generation Routes for Library Management System.
Uses SQLAlchemy to aggregate data for various inventory and financial reports.
"""
from datetime import datetime
from flask import Blueprint, render_template
from sqlalchemy import func
from app.models.book import Book
from app.utils.db import db

# Initialize the Blueprint for reports
report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports/inventory')
def inventory_report():
    """
    Generates an overall inventory report.
    Calculates total books in the system vs. currently available books.
    """
    # Summing up quantities across all book records
    total_books_count = db.session.query(func.sum(Book.quantity)).scalar() or 0
    available_books_count = db.session.query(func.sum(Book.available_quantity)).scalar() or 0
    
    return render_template('reports/inventory.html', 
                           total=total_books_count, 
                           available=available_books_count)

@report_bp.route('/reports/issued')
def issued_books_report():
    """
    Generates a report of all books currently issued to members.
    """
    from app.models.lending import Lending
    # Currently issued books have no return_date
    issued_list = Lending.query.filter(Lending.return_date.is_(None)).all()
    total_issued = len(issued_list)
    
    return render_template('reports/issued.html', 
                           items=issued_list, 
                           total=total_issued)

@report_bp.route('/reports/late')
def late_returns_report():
    """
    Generates a report of overdue books that haven't been returned yet.
    """
    from app.models.lending import Lending
    now = datetime.utcnow()
    
    # Overdue books are those without a return_date where the due_date has passed
    # Assumes Lending model has a 'due_date' column
    late_list = Lending.query.filter(
        Lending.return_date.is_(None),
        Lending.due_date < now
    ).all()
    
    return render_template('reports/late.html', items=late_list)

@report_bp.route('/reports/fines')
def fine_report():
    """
    Generates a financial report of total fines generated.
    """
    from app.models.fine import Fine
    
    # Aggregate fine amounts
    total_fines = db.session.query(func.sum(Fine.amount)).scalar() or 0
    unpaid_fines = db.session.query(func.sum(Fine.amount)).filter(Fine.status == 'unpaid').scalar() or 0
    paid_fines = db.session.query(func.sum(Fine.amount)).filter(Fine.status == 'paid').scalar() or 0
    
    return render_template('reports/fines.html', 
                           total=total_fines, 
                           unpaid=unpaid_fines, 
                           paid=paid_fines)
