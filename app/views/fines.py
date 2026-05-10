"""
Fine Management View for Library Management System.
Provides a desktop interface to monitor and manage library fines using Tkinter and SQL Server.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.models.member import Member
from app.utils.db import db

class FineManagementView:
    """
    Interface for tracking member fines.
    Allows administrators to view outstanding debts and search records by member.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Fine Management Module")
        self.root.geometry("850x550")
        self.root.configure(bg="#FDFDFD")

        self._setup_ui()
        self.load_fines()

    def _setup_ui(self):
        """
        Initializes search controls and the data table.
        """
        # Header
        header = tk.Frame(self.root, bg="#ECEFF1", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="Member Fine Records", font=("Helvetica", 14, "bold"), bg="#ECEFF1").pack()

        # Search Controls
        search_frame = tk.Frame(self.root, bg="#FDFDFD", padx=20, pady=15)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="Search Member (Name/ID):", bg="#FDFDFD").pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=35).pack(side="left", padx=10)
        
        tk.Button(search_frame, text="Search", command=self.search_fines, width=10).pack(side="left")
        tk.Button(search_frame, text="Show Unpaid", command=self.filter_unpaid, width=12, bg="#E91E63", fg="white").pack(side="left", padx=5)
        tk.Button(search_frame, text="Refresh All", command=self.load_fines, width=10).pack(side="left")

        # Fine Table
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Fine ID", "Member ID", "Member Name", "Amount", "Status", "Created Date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Column configuration
        widths = [70, 80, 200, 100, 100, 150]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[i], anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def load_fines(self, fines_data=None):
        """
        Populates the Treeview with fine records from SQL Server.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            from app.models.fine import Fine
            
            if fines_data is None:
                fines_data = Fine.query.all()

            for fine in fines_data:
                # Fetch member details for the record
                member = Member.query.get(fine.member_id)
                member_name = member.full_name if member else "Unknown Member"
                
                self.tree.insert("", "end", values=(
                    fine.id,
                    fine.member_id,
                    member_name,
                    f"${fine.amount:.2f}",
                    fine.status.upper(),
                    fine.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(fine, 'created_at') else "N/A"
                ))
        except ImportError:
            messagebox.showerror("Error", "Fine model not found.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load fines: {e}")

    def filter_unpaid(self):
        """
        Quick filter to show only pending/unpaid fines.
        """
        from app.models.fine import Fine
        unpaid = Fine.query.filter_by(status='unpaid').all()
        self.load_fines(unpaid)

    def search_fines(self):
        """
        Filters fines by member name or member ID.
        """
        query = self.search_var.get().strip()
        if not query:
            self.load_fines()
            return

        from app.models.fine import Fine
        
        # Search by ID if numeric, else search by member name join
        try:
            if query.isdigit():
                results = Fine.query.filter_by(member_id=int(query)).all()
            else:
                # Filter via relationship or member name search
                results = Fine.query.join(Member).filter(Member.full_name.ilike(f"%{query}%")).all()
            
            self.load_fines(results)
        except Exception as e:
            messagebox.showerror("Search Error", str(e))
