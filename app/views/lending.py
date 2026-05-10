"""
Lending View for Library Management System.
Provides a Tkinter interface for issuing books to library members.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.models.book import Book
from app.models.member import Member
from app.utils.db import db

class LendingManagementView:
    """
    Interface for processing book loans.
    Ensures data integrity by checking availability and updating inventory.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Book Lending Module")
        self.root.geometry("500x450")
        self.root.configure(bg="#FDFDFD")

        # Data Storage
        self.members_list = []
        self.books_list = []

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        """
        Creates the layout and widgets for the lending form.
        """
        main_frame = tk.Frame(self.root, bg="#FDFDFD", padx=30, pady=30)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Issue a New Book", font=("Helvetica", 16, "bold"), bg="#FDFDFD", fg="#333").pack(pady=(0, 20))

        # Member Selection
        tk.Label(main_frame, text="Select Member:", bg="#FDFDFD").pack(anchor="w")
        self.member_combo = ttk.Combobox(main_frame, state="readonly", width=45)
        self.member_combo.pack(pady=(5, 15))

        # Book Selection
        tk.Label(main_frame, text="Select Book:", bg="#FDFDFD").pack(anchor="w")
        self.book_combo = ttk.Combobox(main_frame, state="readonly", width=45)
        self.book_combo.pack(pady=(5, 15))

        # Issue Date (Read-only for current date)
        tk.Label(main_frame, text="Issue Date:", bg="#FDFDFD").pack(anchor="w")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(main_frame, textvariable=self.date_var, width=48, state="readonly").pack(pady=(5, 15))

        # Action Button
        self.issue_btn = tk.Button(
            main_frame, 
            text="Issue Book", 
            command=self.process_lending, 
            bg="#2196F3", 
            fg="white", 
            font=("Helvetica", 10, "bold"),
            pady=8
        )
        self.issue_btn.pack(fill="x", pady=20)

    def refresh_data(self):
        """
        Updates the comboboxes with current data from SQL Server.
        """
        try:
            # Fetch all members
            self.members_list = Member.query.all()
            self.member_combo['values'] = [f"{m.id} | {m.full_name}" for m in self.members_list]

            # Fetch only books that have available stock
            self.books_list = Book.query.filter(Book.available_quantity > 0).all()
            self.book_combo['values'] = [f"{b.id} | {b.title} (Stock: {b.available_quantity})" for b in self.books_list]
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load records: {e}")

    def process_lending(self):
        """
        Validates the transaction and updates the database records.
        """
        member_selection = self.member_combo.get()
        book_selection = self.book_combo.get()

        if not member_selection or not book_selection:
            messagebox.showwarning("Incomplete Form", "Please select both a member and a book.")
            return

        # Extract IDs from the combobox strings
        member_id = int(member_selection.split(" | ")[0])
        book_id = int(book_selection.split(" | ")[0])

        try:
            # This logic assumes an app.models.lending.Lending model exists
            from app.models.lending import Lending
            
            book = Book.query.get(book_id)
            
            # Double-check availability before issuing
            if book.available_quantity <= 0:
                messagebox.showerror("Out of Stock", "This book is no longer available.")
                self.refresh_data()
                return

            # Create Lending record
            new_loan = Lending(
                member_id=member_id,
                book_id=book_id,
                issue_date=datetime.now()
            )
            
            # Update inventory automatically
            book.available_quantity -= 1
            
            db.session.add(new_loan)
            db.session.commit()
            
            messagebox.showinfo("Success", f"Book successfully issued to member ID {member_id}.")
            self.refresh_data()
            self.member_combo.set("")
            self.book_combo.set("")

        except ImportError:
            messagebox.showerror("Configuration Error", "Lending model not found. Please ensure app/models/lending.py exists.")
        except Exception as e:
            db.session.rollback()
            messagebox.showerror("Transaction Error", f"Failed to issue book: {e}")
