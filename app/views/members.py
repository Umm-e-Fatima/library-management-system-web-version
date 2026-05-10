"""
Member Management View for Library Management System.
Handles administrative operations for library members through a Tkinter interface.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.models.member import Member
from app.utils.db import db

class MembersManagementView:
    """
    Main interface for managing library members.
    Supports viewing, adding, updating, searching, and deleting member records.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Members Management")
        self.root.geometry("1000x650")
        self.root.configure(bg="#F5F5F5")

        # UI Components Initialization
        self._setup_input_form()
        self._setup_search_bar()
        self._setup_data_table()
        
        # Initial data load
        self.load_data()

    def _setup_input_form(self):
        """
        Creates the labels and entry widgets for member data input.
        """
        form_frame = tk.LabelFrame(self.root, text="Member Information", font=("Arial", 10, "bold"), bg="#F5F5F5", pady=10, padx=10)
        form_frame.pack(fill="x", padx=20, pady=10)

        # Layout for Input Fields
        labels = ["Full Name", "Email", "Phone", "Address"]
        self.vars = {label: tk.StringVar() for label in labels}
        
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=f"{label}:", bg="#F5F5F5").grid(row=0, column=i*2, sticky="e", padx=5)
            tk.Entry(form_frame, textvariable=self.vars[label], width=18).grid(row=0, column=i*2+1, padx=5)

        # Action Buttons
        btn_frame = tk.Frame(form_frame, bg="#F5F5F5")
        btn_frame.grid(row=1, column=0, columnspan=8, pady=15)

        tk.Button(btn_frame, text="Add Member", command=self.add_member, bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Member", command=self.update_member, bg="#2196F3", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Member", command=self.delete_member, bg="#F44336", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear Fields", command=self.clear_fields, width=12).pack(side="left", padx=5)

    def _setup_search_bar(self):
        """
        Creates the search interface for filtering members.
        """
        search_frame = tk.Frame(self.root, bg="#F5F5F5")
        search_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(search_frame, text="Search Member:", bg="#F5F5F5", font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=50).pack(side="left", padx=10)
        tk.Button(search_frame, text="Search", command=self.search_members, width=10).pack(side="left")
        tk.Button(search_frame, text="Refresh", command=self.load_data, width=10).pack(side="left", padx=5)

    def _setup_data_table(self):
        """
        Initializes the ttk.Treeview to display member records.
        """
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Name", "Email", "Phone", "Address", "Join Date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Formatting headings and columns
        column_widths = [50, 200, 200, 120, 200, 150]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[i], anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def load_data(self, members=None):
        """
        Fetches member records from the database and populates the table.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        if members is None:
            members = Member.query.all()

        for member in members:
            self.tree.insert("", "end", values=(
                member.id, member.full_name, member.email,
                member.phone, member.address, member.membership_date.strftime("%Y-%m-%d %H:%M")
            ))

    def add_member(self):
        """
        Adds a new member to the SQL Server database.
        """
        try:
            new_member = Member(
                full_name=self.vars["Full Name"].get(),
                email=self.vars["Email"].get(),
                phone=self.vars["Phone"].get(),
                address=self.vars["Address"].get()
            )
            db.session.add(new_member)
            db.session.commit()
            messagebox.showinfo("Success", "Member registered successfully.")
            self.load_data()
            self.clear_fields()
        except Exception as e:
            db.session.rollback()
            messagebox.showerror("Error", f"Failed to add member: {e}")

    def update_member(self):
        """
        Updates the details of the selected member.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a member to update.")
            return

        try:
            member_id = self.tree.item(selected_item[0])["values"][0]
            member = Member.query.get(member_id)
            if member:
                member.full_name = self.vars["Full Name"].get()
                member.email = self.vars["Email"].get()
                member.phone = self.vars["Phone"].get()
                member.address = self.vars["Address"].get()
                
                db.session.commit()
                messagebox.showinfo("Success", "Member updated successfully.")
                self.load_data()
        except Exception as e:
            db.session.rollback()
            messagebox.showerror("Error", f"Update failed: {e}")

    def delete_member(self):
        """
        Removes the selected member from the database.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            return

        if messagebox.askyesno("Confirm Delete", "Permanently remove this member?"):
            try:
                member_id = self.tree.item(selected_item[0])["values"][0]
                member = Member.query.get(member_id)
                if member:
                    db.session.delete(member)
                    db.session.commit()
                    self.load_data()
            except Exception as e:
                db.session.rollback()
                messagebox.showerror("Error", f"Deletion failed: {e}")

    def search_members(self):
        """
        Filters members by name or email.
        """
        query = self.search_var.get()
        filtered = Member.query.filter(
            (Member.full_name.ilike(f'%{query}%')) | 
            (Member.email.ilike(f'%{query}%'))
        ).all()
        self.load_data(filtered)

    def on_select(self, event):
        """
        Fills the form with data from the selected row.
        """
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])["values"]
            self.vars["Full Name"].set(values[1])
            self.vars["Email"].set(values[2])
            self.vars["Phone"].set(values[3])
            self.vars["Address"].set(values[4])

    def clear_fields(self):
        """
        Resets the input form.
        """
        for var in self.vars.values():
            var.set("")
