"""
Book Lending and Return JSON API.
Handles the automated process of issuing books, processing returns, 
calculating fines, and updating inventory via RESTful endpoints.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.book import Book
from app.models.member import Member
from app.utils.db import db

# Initialize the Blueprint for the Lending API
lending_api_bp = Blueprint('lending_api', __name__)

@lending_api_bp.route('/api/lending/issue', methods=['POST'])
def api_issue_book():
    """
    API endpoint to issue a book to a member.
    JSON Body: { "book_id": int, "member_id": int }
    """
    from app.models.lending import Lending
    data = request.get_json()
    
    if not data or not data.get('book_id') or not data.get('member_id'):
        return jsonify({'error': 'book_id and member_id are required'}), 400

    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if book.available_quantity <= 0:
        return jsonify({'error': 'Book currently out of stock'}), 400

    # Create the lending record
    new_loan = Lending(
        book_id=book.id,
        member_id=data['member_id'],
        issue_date=datetime.utcnow()
    )
    
    # Inventory update: reduce available quantity
    book.available_quantity -= 1
    
    try:
        db.session.add(new_loan)
        db.session.commit()
        return jsonify({
            'message': 'Book issued successfully',
            'lending_id': new_loan.id,
            'new_available_qty': book.available_quantity
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lending_api_bp.route('/api/lending/return/<int:lending_id>', methods=['POST'])
def api_return_book(lending_id):
    """
    API endpoint to process a book return and calculate any overdue fines.
    """
    from app.models.lending import Lending
    from app.models.fine import Fine
    
    lending = Lending.query.get_or_404(lending_id)
    
    if lending.return_date:
        return jsonify({'error': 'Book already returned'}), 400

    now = datetime.utcnow()
    lending.return_date = now
    
    # Inventory update: increase available quantity
    book = Book.query.get(lending.book_id)
    if book:
        book.available_quantity += 1
        
    # Fine calculation API logic
    fine_amount = 0
    if hasattr(lending, 'due_date') and lending.due_date and now > lending.due_date:
        days_late = (now - lending.due_date).days
        if days_late > 0:
            fine_amount = days_late * 5.0  # $5 per day fine rate
            
            new_fine = Fine(
                lending_id=lending.id,
                member_id=lending.member_id,
                amount=fine_amount,
                status='unpaid'
            )
            db.session.add(new_fine)

    try:
        db.session.commit()
        return jsonify({
            'message': 'Book returned successfully',
            'fine_calculated': fine_amount,
            'status': 'returned'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lending_api_bp.route('/api/lending/status/<int:book_id>', methods=['GET'])
def get_lending_status(book_id):
    """
    Utility endpoint to check the current inventory status of a book.
    """
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'book_id': book.id,
        'total_quantity': book.quantity,
        'available_quantity': book.available_quantity
    })
