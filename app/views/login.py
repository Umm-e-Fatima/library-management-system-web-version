"""
Login View for Library Management System.
Implements a desktop-based login interface using Tkinter and SQL Server authentication.
"""
import tkinter as tk
from tkinter import messagebox
from werkzeug.security import check_password_hash
from app.models.user import User
from app.utils.db import db

class LoginWindow:
    """
    A class to represent the Tkinter login window.
    Handles admin authentication by verifying credentials against the SQL Server database.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("LMS Admin Login")
        self.root.geometry("380x280")
        self.root.resizable(False, False)
        
        # Center the window on the screen
        self._center_window()
        
        # Initialize UI components
        self._setup_ui()

    def _center_window(self):
        """
        Utility to center the Tkinter window on the screen.
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_ui(self):
        """
        Defines the layout and components of the login interface.
        """
        # Title Label
        tk.Label(self.root, text="Library Management System", font=("Segoe UI", 16, "bold")).pack(pady=20)

        # Container for inputs
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20)

        # Username Field
        tk.Label(input_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(input_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        # Password Field
        tk.Label(input_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(input_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Login Button
        self.login_button = tk.Button(
            self.root, 
            text="Login", 
            command=self.authenticate, 
            width=20, 
            bg="#0078D4", 
            fg="white", 
            font=("Segoe UI", 10, "bold")
        )
        self.login_button.pack(pady=20)

    def authenticate(self):
        """
        Performs authentication by checking provided credentials against the User model.
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        try:
            # Query the database for the user record
            # Assumes an active application context if using Flask-SQLAlchemy
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                messagebox.showinfo("Login Success", f"Welcome, {user.username}!")
                # Proceed to the next window/module
                self.root.destroy()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
                
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to authenticate: {str(e)}")

# This class can be instantiated by passing a tk.Tk() instance
