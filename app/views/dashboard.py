"""
Dashboard View for Library Management System.
Serves as the central navigation hub for administrative tasks using Tkinter.
"""
import tkinter as tk
from tkinter import messagebox

class DashboardWindow:
    """
    Main Dashboard class that organizes the application into a professional layout.
    Features a persistent sidebar for navigation and a dynamic main content area.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F4F7F6")
        
        # Design Tokens
        self.sidebar_bg = "#2C3E50"
        self.active_btn_bg = "#3498DB"
        self.btn_fg = "#FFFFFF"
        self.header_font = ("Helvetica", 18, "bold")
        self.nav_font = ("Helvetica", 11)

        # Build UI Structure
        self._create_sidebar()
        self._create_main_container()

    def _create_sidebar(self):
        """
        Constructs the side navigation bar with operational modules.
        """
        sidebar = tk.Frame(self.root, bg=self.sidebar_bg, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Dashboard Brand/Title
        tk.Label(
            sidebar, 
            text="LMS ADMIN", 
            bg=self.sidebar_bg, 
            fg=self.btn_fg, 
            font=self.header_font, 
            pady=40
        ).pack()

        # Navigation menu items
        menu_items = [
            ("Books", self.show_books),
            ("Members", self.show_members),
            ("Lending", self.show_lending),
            ("Returns", self.show_returns),
            ("Reports", self.show_reports),
            ("Fines", self.show_fines),
            ("Logout", self.perform_logout)
        ]

        for text, command in menu_items:
            # Styled button for each module
            btn = tk.Button(
                sidebar,
                text=text,
                command=command,
                bg=self.sidebar_bg,
                fg=self.btn_fg,
                font=self.nav_font,
                bd=0,
                padx=20,
                pady=15,
                anchor="w",
                activebackground=self.active_btn_bg,
                activeforeground=self.btn_fg,
                cursor="hand2"
            )
            btn.pack(fill="x")

    def _create_main_container(self):
        """
        Initializes the main content area where different module views will be displayed.
        """
        self.main_area = tk.Frame(self.root, bg="#F4F7F6")
        self.main_area.pack(side="right", fill="both", expand=True)

        # Initial Welcome Message
        welcome_lbl = tk.Label(
            self.main_area, 
            text="Welcome to the Administration Dashboard", 
            font=("Helvetica", 16),
            bg="#F4F7F6",
            fg="#7F8C8D"
        )
        welcome_lbl.pack(expand=True)

    # Navigation Methods (Placeholders for module integration)
    def show_books(self):
        messagebox.showinfo("Info", "Opening Books Management...")

    def show_members(self):
        messagebox.showinfo("Info", "Opening Members Management...")

    def show_lending(self):
        messagebox.showinfo("Info", "Opening Lending Module...")

    def show_returns(self):
        messagebox.showinfo("Info", "Opening Returns Module...")

    def show_reports(self):
        messagebox.showinfo("Info", "Generating Reports...")

    def show_fines(self):
        messagebox.showinfo("Info", "Viewing Fines Records...")

    def perform_logout(self):
        """
        Handles the logout process and closes the dashboard.
        """
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.root.destroy()

# Initialization logic
if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardWindow(root)
    root.mainloop()
