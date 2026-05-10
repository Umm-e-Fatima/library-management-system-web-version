"""
Reports View for Library Management System.
Aggregates and displays comprehensive library data including inventory, lending status, and fines using Tkinter.
"""
import tkinter as tk
from tkinter import ttk
from sqlalchemy import func
from app.models.book import Book
from app.utils.db import db

class ReportsManagementView:
    """
    Interface for viewing administrative reports.
    Uses tabs to organize different data views like Issued Books, Overdue Items, and Fines.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Library Inventory & Financial Reports")
        self.root.geometry("1000x750")
        self.root.configure(bg="#ECEFF1")

        self._setup_summary_panel()
        self._setup_report_tabs()
        
        # Load initial report data
        self.refresh_reports()

    def _setup_summary_panel(self):
        """
        Creates a top panel showing high-level stats.
        """
        panel = tk.Frame(self.root, bg="#263238", pady=15)
        panel.pack(fill="x")

        title_lbl = tk.Label(panel, text="Inventory Dashboard", fg="white", bg="#263238", font=("Helvetica", 14, "bold"))
        title_lbl.pack(side="left", padx=20)

        self.total_books_var = tk.StringVar(value="Total Books: 0")
        self.avail_books_var = tk.StringVar(value="Available: 0")

        tk.Label(panel, textvariable=self.total_books_var, fg="#81C784", bg="#263238", font=("Helvetica", 11)).pack(side="left", padx=20)
        tk.Label(panel, textvariable=self.avail_books_var, fg="#64B5F6", bg="#263238", font=("Helvetica", 11)).pack(side="left", padx=20)

        tk.Button(panel, text="Refresh Data", command=self.refresh_reports, bg="#455A64", fg="white", relief="flat").pack(side="right", padx=20)

    def _setup_report_tabs(self):
        """
        Organizes detailed reports into a tabbed notebook interface.
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Issued Books Tab
        self.issued_tree = self._create_table_tab("Currently Issued", ("Lending ID", "Book ID", "Member ID", "Issue Date"))
        
        # 2. Late Returns Tab
        self.late_tree = self._create_table_tab("Late Returns", ("Lending ID", "Book Title", "Member Name", "Due Date"))
        
        # 3. Fines Tab
        self.fine_tree = self._create_table_tab("Fine Records", ("Fine ID", "Member ID", "Amount", "Status", "Date"))

    def _create_table_tab(self, tab_name, columns):
        """
        Helper to create a scrollable Treeview within a notebook tab.
        """
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text=tab_name)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def refresh_reports(self):
        """
        Queries SQL Server and updates all reports and labels.
        """
        try:
            # Summary stats
            total_qty = db.session.query(func.sum(Book.quantity)).scalar() or 0
            avail_qty = db.session.query(func.sum(Book.available_quantity)).scalar() or 0
            self.total_books_var.set(f"Total Books: {total_qty}")
            self.avail_books_var.set(f"Available: {avail_qty}")

            # Dynamic imports for lending and fine models
            from app.models.lending import Lending
            from app.models.fine import Fine
            from datetime import datetime

            # Populate Issued Books
            self._fill_tree(self.issued_tree, Lending.query.filter(Lending.return_date.is_(None)).all(), 
                            lambda l: (l.id, l.book_id, l.member_id, l.issue_date.strftime("%Y-%m-%d")))

            # Populate Late Returns
            now = datetime.now()
            # Logic assumes 'due_date' exists in Lending model
            late_records = Lending.query.filter(Lending.return_date.is_(None), Lending.due_date < now).all()
            self._fill_tree(self.late_tree, late_records, 
                            lambda l: (l.id, f"Book {l.book_id}", f"Member {l.member_id}", l.due_date.strftime("%Y-%m-%d")))

            # Populate Fines
            self._fill_tree(self.fine_tree, Fine.query.all(), 
                            lambda f: (f.id, f.member_id, f"${f.amount:.2f}", f.status.upper(), f.created_at.strftime("%Y-%m-%d")))

        except Exception as e:
            print(f"Report Error: {e}")

    def _fill_tree(self, tree, data_list, mapping_func):
        """
        Utility to clear and repopulate a Treeview.
        """
        for item in tree.get_children():
            tree.delete(item)
        for data in data_list:
            tree.insert("", "end", values=mapping_func(data))

# Example usage
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ReportsManagementView(root)
#     root.mainloop()
