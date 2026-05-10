"""
Books Management View for Library Management System.
Handles book-related CRUD operations through a desktop interface using Tkinter and SQLAlchemy.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.models.book import Book
from app.utils.db import db

class BooksManagementView:
    """
    Main interface for managing library books.
    Supports viewing, adding, updating, searching, and deleting book records.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Books Management System")
        self.root.geometry("1000x650")
        self.root.configure(bg="#F0F0F0")

        # UI Components Initialization
        self._setup_input_form()
        self._setup_search_bar()
        self._setup_data_table()
        
        # Initial data load
        self.load_data()

    def _setup_input_form(self):
        """
        Creates the labels and entry widgets for book data input.
        """
        form_frame = tk.LabelFrame(self.root, text="Book Information", font=("Arial", 10, "bold"), bg="#F0F0F0", pady=10, padx=10)
        form_frame.pack(fill="x", padx=20, pady=10)

        # Grid Layout for Input Fields
        labels = ["Title", "Author", "Category", "Quantity", "Year"]
        self.vars = {label: tk.StringVar() for label in labels}
        
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=f"{label}:", bg="#F0F0F0").grid(row=0, column=i*2, sticky="e", padx=5)
            tk.Entry(form_frame, textvariable=self.vars[label], width=15).grid(row=0, column=i*2+1, padx=5)

        # Button Group
        btn_frame = tk.Frame(form_frame, bg="#F0F0F0")
        btn_frame.grid(row=1, column=0, columnspan=10, pady=15)

        tk.Button(btn_frame, text="Add Book", command=self.add_book, bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Book", command=self.update_book, bg="#2196F3", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Book", command=self.delete_book, bg="#F44336", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear Fields", command=self.clear_fields, width=12).pack(side="left", padx=5)

    def _setup_search_bar(self):
        """
        Creates the search interface for filtering books.
        """
        search_frame = tk.Frame(self.root, bg="#F0F0F0")
        search_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(search_frame, text="Search Book:", bg="#F0F0F0", font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=50).pack(side="left", padx=10)
        tk.Button(search_frame, text="Search", command=self.search_books, width=10).pack(side="left")
        tk.Button(search_frame, text="Refresh", command=self.load_data, width=10).pack(side="left", padx=5)

    def _setup_data_table(self):
        """
        Initializes the ttk.Treeview to display book records.
        """
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Title", "Author", "Category", "Qty", "Available", "Year")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Formatting headings and columns
        column_widths = [50, 250, 150, 100, 50, 70, 60]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[i], anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def load_data(self, books=None):
        """
        Fetches book records from the database and populates the table.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        if books is None:
            books = Book.query.all()

        for book in books:
            self.tree.insert("", "end", values=(
                book.id, book.title, book.author, book.category,
                book.quantity, book.available_quantity, book.published_year
            ))

    def add_book(self):
        """
        Validates input and adds a new book to the SQL Server database.
        """
        try:
            new_book = Book(
                title=self.vars["Title"].get(),
                author=self.vars["Author"].get(),
                category=self.vars["Category"].get(),
                quantity=int(self.vars["Quantity"].get() or 0),
                available_quantity=int(self.vars["Quantity"].get() or 0),
                published_year=int(self.vars["Year"].get() or 0)
            )
            db.session.add(new_book)
            db.session.commit()
            messagebox.showinfo("Success", "Book record added successfully.")
            self.load_data()
            self.clear_fields()
        except ValueError:
            messagebox.showwarning("Input Error", "Quantity and Year must be numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book: {e}")

    def update_book(self):
        """
        Updates the details of the selected book.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book to update.")
            return

        try:
            book_id = self.tree.item(selected_item[0])["values"][0]
            book = Book.query.get(book_id)
            if book:
                book.title = self.vars["Title"].get()
                book.author = self.vars["Author"].get()
                book.category = self.vars["Category"].get()
                book.quantity = int(self.vars["Quantity"].get())
                book.published_year = int(self.vars["Year"].get())
                
                db.session.commit()
                messagebox.showinfo("Success", "Book record updated.")
                self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")

    def delete_book(self):
        """
        Removes the selected book from the database.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            try:
                book_id = self.tree.item(selected_item[0])["values"][0]
                book = Book.query.get(book_id)
                if book:
                    db.session.delete(book)
                    db.session.commit()
                    self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Deletion failed: {e}")

    def search_books(self):
        """
        Filters the books list based on search keywords.
        """
        query = self.search_var.get()
        filtered_books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%'))
        ).all()
        self.load_data(filtered_books)

    def on_select(self, event):
        """
        Fills the form with data from the selected table row.
        """
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])["values"]
            self.vars["Title"].set(values[1])
            self.vars["Author"].set(values[2])
            self.vars["Category"].set(values[3])
            self.vars["Quantity"].set(values[4])
            self.vars["Year"].set(values[6])

    def clear_fields(self):
        """
        Resets all input fields.
        """
        for var in self.vars.values():
            var.set("")
