"""
Book Management JSON API.
Provides RESTful endpoints for CRUD operations on the Book model.
"""
from flask import Blueprint, request, jsonify
from app.models.book import Book
from app.utils.db import db

# Initialize the Blueprint for the Book API
book_api_bp = Blueprint('book_api', __name__)

@book_api_bp.route('/api/books', methods=['GET'])
def get_books():
    """
    Retrieves all books and returns them as a JSON array.
    """
    books = Book.query.all()
    book_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'category': book.category,
        'quantity': book.quantity,
        'available_quantity': book.available_quantity,
        'published_year': book.published_year
    } for book in books]
    
    return jsonify(book_list)

@book_api_bp.route('/api/books', methods=['POST'])
def add_book():
    """
    Adds a new book record from JSON input.
    """
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({'error': 'Title and Author are required fields'}), 400

    new_book = Book(
        title=data.get('title'),
        author=data.get('author'),
        category=data.get('category'),
        quantity=data.get('quantity', 1),
        available_quantity=data.get('quantity', 1),
        published_year=data.get('published_year')
    )

    try:
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully', 'book_id': new_book.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@book_api_bp.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    """
    Updates an existing book record based on JSON input.
    """
    book = Book.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    # Selective updates
    if 'title' in data: book.title = data['title']
    if 'author' in data: book.author = data['author']
    if 'category' in data: book.category = data['category']
    if 'quantity' in data: book.quantity = data['quantity']
    if 'published_year' in data: book.published_year = data['published_year']

    try:
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@book_api_bp.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    """
    Deletes a book record from the system.
    """
    book = Book.query.get_or_404(id)
    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
