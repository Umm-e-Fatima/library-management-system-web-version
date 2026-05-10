"""
Main Application Entry Point.

Initializes the Flask application, registers all functional blueprints, 
and starts the development server for the Library Management System.
"""
from flask import redirect, url_for
from app import create_app

# Import blueprints from the routes package
from app.routes.auth_routes import auth_bp
from app.routes.book_routes import book_bp
from app.routes.member_routes import member_bp
from app.routes.lending_routes import lending_bp
from app.routes.return_routes import return_bp
from app.routes.report_routes import report_bp

# Initialize the Flask application using the factory function
# The SQL Server configuration is handled within the app factory
app = create_app()

# Register all application Blueprints
# Organizing routes under specific URL prefixes for clarity
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(book_bp, url_prefix='/books')
app.register_blueprint(member_bp, url_prefix='/members')
app.register_blueprint(lending_bp, url_prefix='/lending')
app.register_blueprint(return_bp, url_prefix='/returns')
app.register_blueprint(report_bp, url_prefix='/reports')

@app.route('/')
def index():
    """
    Root route for the application.
    Redirects users to the books view as the default landing page.
    """
    return redirect(url_for('books.view_books'))

if __name__ == '__main__':
    """
    Starts the Flask development server on port 5000.
    """
    # Running on 0.0.0.0 makes the server accessible within a local network
    app.run(host='0.0.0.0', port=5000, debug=True)
