"""
Returns Management View for Library Management System.
Implements a desktop interface for processing book returns and managing late fees.
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from app.models.book import Book
from app.utils.db import db

class ReturnsManagementView:
    """
    Interface for library administrators to process book returns.
    Automatically handles inventory restocking and overdue fine calculations.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Book Return Module")
        self.root.geometry("450x400")
        self.root.configure(bg="#F9F9F9")

        self._setup_ui()

    def _setup_ui(self):
        """
        Creates the layout for the return processing form.
        """
        main_frame = tk.Frame(self.root, bg="#F9F9F9", padx=40, pady=40)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="Process Book Return", font=("Helvetica", 16, "bold"), bg="#F9F9F9").pack(pady=(0, 25))

        # Lending ID Input
        tk.Label(main_frame, text="Enter Lending ID:", bg="#F9F9F9", font=("Helvetica", 10)).pack(anchor="w")
        self.lending_id_var = tk.StringVar()
        self.lending_id_entry = tk.Entry(main_frame, textvariable=self.lending_id_var, width=40, font=("Helvetica", 11))
        self.lending_id_entry.pack(pady=(5, 20))

        # Action Button
        self.return_btn = tk.Button(
            main_frame, 
            text="Confirm Return", 
            command=self.process_return, 
            bg="#FF9800", 
            fg="white", 
            font=("Helvetica", 11, "bold"),
            pady=10,
            cursor="hand2"
        )
        self.return_btn.pack(fill="x", pady=10)

        # Result Display Area (Optional/Status)
        self.status_label = tk.Label(main_frame, text="", bg="#F9F9F9", font=("Helvetica", 9, "italic"))
        self.status_label.pack(pady=15)

    def process_return(self):
        """
        Validates the lending record, calculates fines, and updates the SQL Server database.
        """
        lending_id_str = self.lending_id_var.get().strip()

        if not lending_id_str or not lending_id_str.isdigit():
            messagebox.showwarning("Input Error", "Please enter a valid numeric Lending ID.")
            return

        lending_id = int(lending_id_str)

        try:
            # Dynamic import to ensure Lending model is accessible
            from app.models.lending import Lending
            from app.models.fine import Fine

            # Retrieve the lending transaction
            lending = Lending.query.get(lending_id)

            if not lending:
                messagebox.showerror("Error", f"No record found for Lending ID: {lending_id}")
                return

            if lending.return_date:
                messagebox.showinfo("Status", "This book has already been returned.")
                return

            # 1. Update Return Date
            current_time = datetime.now()
            lending.return_date = current_time

            # 2. Update Book Inventory
            book = Book.query.get(lending.book_id)
            if book:
                book.available_quantity += 1

            # 3. Automatic Fine Calculation
            fine_msg = ""
            # Assumes 'due_date' field exists in Lending model
            if hasattr(lending, 'due_date') and lending.due_date:
                if current_time > lending.due_date:
                    overdue_days = (current_time - lending.due_date).days
                    if overdue_days > 0:
                        amount = overdue_days * 5.0 # $5.00 fine per day
                        
                        # Create Fine record if model exists
                        new_fine = Fine(
                            lending_id=lending.id,
                            member_id=lending.member_id,
                            amount=amount,
                            status='unpaid'
                        )
                        db.session.add(new_fine)
                        fine_msg = f"\n\nLATE RETURN!\nOverdue Days: {overdue_days}\nTotal Fine: ${amount:.2f}"

            # Commit changes to database
            db.session.commit()
            
            messagebox.showinfo("Return Successful", f"Book '{book.title if book else 'ID '+str(lending.book_id)}' returned.{fine_msg}")
            self.lending_id_var.set("")
            self.status_label.config(text=f"Last processed ID: {lending_id}", fg="green")

        except Exception as e:
            db.session.rollback()
            messagebox.showerror("Transaction Error", f"Failed to process return: {e}")
