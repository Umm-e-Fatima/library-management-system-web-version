"""
Lending Management Routes for Library Management System.
Handles the process of issuing books to members and tracking active loans.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.book import Book
from app.models.member import Member
from app.utils.db import db

# Initialize the Blueprint for lending
lending_bp = Blueprint('lending', __name__)

@lending_bp.route('/lending/issue', methods=['GET', 'POST'])
def issue_book():
    """
    Handles issuing a book to a member.
    Verifies availability, creates a lending record, and updates inventory.
    """
    # Local import to avoid circular dependency if Lending is defined later
    from app.models.lending import Lending

    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        member_id = request.form.get('member_id', type=int)

        book = Book.query.get_or_404(book_id)
        member = Member.query.get_or_404(member_id)

        # Inventory check: prevent issuing unavailable books
        if book.available_quantity <= 0:
            flash(f"Sorry, '{book.title}' is currently out of stock.", "warning")
            return redirect(url_for('lending.issue_book'))

        # Create a new lending record
        new_lending = Lending(
            book_id=book.id,
            member_id=member.id,
            issue_date=datetime.utcnow()
        )
        
        # Automatically reduce available inventory
        book.available_quantity -= 1

        try:
            db.session.add(new_lending)
            db.session.commit()
            flash(f"Book '{book.title}' issued successfully to {member.full_name}.", "success")
            return redirect(url_for('lending.view_issued_books'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while issuing the book: {str(e)}", "danger")

    # Fetch data for selection dropdowns
    available_books = Book.query.filter(Book.available_quantity > 0).all()
    members = Member.query.all()
    return render_template('lending/issue.html', books=available_books, members=members)

@lending_bp.route('/lending/issued')
def view_issued_books():
    """
    Displays a list of all currently issued books.
    """
    from app.models.lending import Lending
    # Retrieve all lending records, typically ordered by most recent
    issued_records = Lending.query.order_by(Lending.issue_date.desc()).all()
    return render_template('lending/view_issued.html', records=issued_records)
