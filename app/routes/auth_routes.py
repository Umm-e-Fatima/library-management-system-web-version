"""
Authentication Routes for Library Management System.
Handles user login, session management, and logout functionality.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.models.user import User

# Initialize the blueprint for authentication
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login requests.
    Validates credentials against the database and manages the user session.
    """
    # If user is already logged in, redirect them away from the login page
    if 'user_id' in session:
        return redirect(url_for('index')) # Adjust redirect as per your main route

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Input validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')

        try:
            # Query the User model for the provided username
            user = User.query.filter_by(username=username).first()
            
            # Check if user exists and verify the hashed password
            if user and check_password_hash(user.password, password):
                # Establish session data
                session.clear()
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                flash(f'Welcome, {user.username}!', 'success')
                # Redirect to a dashboard or home page after successful login
                return redirect(url_for('index'))
            else:
                # Security best practice: avoid revealing whether username or password was incorrect
                flash('Invalid credentials. Please try again.', 'danger')
                
        except Exception as e:
            # Basic error handling for database or connection issues
            # In production, log this error instead of printing
            print(f"Database Error: {e}")
            flash('A database error occurred. Please try again later.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """
    Logs the user out by clearing the session data.
    """
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))
