"""
Book Management Routes for Library Management System.
Implements CRUD operations and search functionality for the Book entity.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.book import Book
from app.utils.db import db

# Initialize the Blueprint for books
book_bp = Blueprint('books', __name__)

@book_bp.route('/books')
def view_books():
    """
    Displays a list of all books in the library.
    """
    books = Book.query.all()
    return render_template('books/view.html', books=books)

@book_bp.route('/books/add', methods=['GET', 'POST'])
def add_book():
    """
    Handles the addition of a new book record.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        quantity = request.form.get('quantity', 1, type=int)
        published_year = request.form.get('published_year', type=int)

        new_book = Book(
            title=title,
            author=author,
            category=category,
            quantity=quantity,
            available_quantity=quantity,  # Initially all copies are available
            published_year=published_year
        )

        try:
            db.session.add(new_book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books.view_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('books/add.html')

@book_bp.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    """
    Updates the information for an existing book.
    """
    book = Book.query.get_or_404(id)

    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.category = request.form.get('category')
        book.quantity = request.form.get('quantity', book.quantity, type=int)
        book.published_year = request.form.get('published_year', type=int)

        try:
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('books.view_books'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('books/update.html', book=book)

@book_bp.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    """
    Removes a book record from the system.
    """
    book = Book.query.get_or_404(id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('books.view_books'))

@book_bp.route('/books/search')
def search_book():
    """
    Filters books based on a search query (title, author, or category).
    """
    query = request.args.get('query', '')
    if query:
        # Search across multiple fields
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) |
            (Book.author.ilike(f'%{query}%')) |
            (Book.category.ilike(f'%{query}%'))
        ).all()
    else:
        books = Book.query.all()

    return render_template('books/view.html', books=books, search_query=query)
