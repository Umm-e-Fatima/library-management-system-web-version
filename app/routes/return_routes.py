"""
Return Management Routes for Library Management System.
Handles book returns, automatic inventory updates, and fine calculations for overdue items.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.book import Book
from app.utils.db import db

# Initialize the Blueprint for book returns
return_bp = Blueprint('returns', __name__)

@return_bp.route('/return/<int:lending_id>', methods=['POST'])
def return_book(lending_id):
    """
    Processes the return of an issued book.
    Increments available inventory and calculates fines if the book is overdue.
    """
    from app.models.lending import Lending
    from app.models.fine import Fine

    lending_record = Lending.query.get_or_404(lending_id)

    # Check if the book has already been returned
    if lending_record.return_date:
        flash("This book has already been recorded as returned.", "warning")
        return redirect(url_for('returns.view_returned_books'))

    # Mark return date as now
    current_time = datetime.utcnow()
    lending_record.return_date = current_time

    # Automatic Inventory Update
    book = Book.query.get(lending_record.book_id)
    if book:
        book.available_quantity += 1

    # Fine Calculation Logic
    # Assumes the Lending model has a 'due_date' attribute
    fine_amount = 0
    if hasattr(lending_record, 'due_date') and lending_record.due_date:
        if current_time > lending_record.due_date:
            days_overdue = (current_time - lending_record.due_date).days
            if days_overdue > 0:
                daily_fine_rate = 5.0  # Example fine amount per day
                fine_amount = days_overdue * daily_fine_rate
                
                # Create and store fine record
                new_fine = Fine(
                    lending_id=lending_record.id,
                    member_id=lending_record.member_id,
                    amount=fine_amount,
                    status='unpaid',
                    created_at=current_time
                )
                db.session.add(new_fine)

    try:
        db.session.commit()
        if fine_amount > 0:
            flash(f"Book returned. An overdue fine of ${fine_amount:.2f} has been registered.", "info")
        else:
            flash("Book returned successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during the return process: {str(e)}", "danger")

    return redirect(url_for('returns.view_returned_books'))

@return_bp.route('/returns')
def view_returned_books():
    """
    Displays a list of all books that have been returned.
    """
    from app.models.lending import Lending
    returned_list = Lending.query.filter(Lending.return_date.isnot(None)).order_by(Lending.return_date.desc()).all()
    return render_template('returns/view.html', records=returned_list)

@return_bp.route('/fines')
def view_fine_records():
    """
    Displays all fine records for library members.
    """
    from app.models.fine import Fine
    all_fines = Fine.query.order_by(Fine.created_at.desc()).all()
    return render_template('returns/fines.html', fines=all_fines)
