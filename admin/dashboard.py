# {
#   "r_email": "",
#   "review": ""
# }
# from pymongo import MongoClient
# def get_admin_db(uri: str = DEFAULT_URI):
#     ...
# from pymongo import MongoClient
# from database import DEFAULT_URI   # <-- FIXED

from database import DB_URI
from pymongo import MongoClient
import tkinter as tk
from tkinter import ttk


def get_admin_db(uri: str = DB_URI):
    client = MongoClient(uri)
    db = client["JewelMart"]
    return db["admin"]

# def get_admin_db(uri: str = DEFAULT_URI):
#     client = MongoClient(uri)
#     db = client["JewelMart"]        # database name
#     return db["admin"]              # admin namespace collection


class AdminDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Dashboard")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Create main label
        tk.Label(self, text="Admin Dashboard", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Create a frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        # Add dashboard buttons
        ttk.Button(button_frame, text="Manage Products", command=self.manage_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Orders", command=self.view_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Manage Users", command=self.manage_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Reports", command=self.view_reports).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)
        
        # Main display area
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        self.mainloop()
    
    def manage_products(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Product Management Panel", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.content_frame, text="Coming soon...").pack()
    
    def view_orders(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Orders Panel", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.content_frame, text="Coming soon...").pack()
    
    def manage_users(self):
        self.clear_content()
        tk.Label(self.content_frame, text="User Management Panel", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.content_frame, text="Coming soon...").pack()
    
    def view_reports(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Reports Panel", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.content_frame, text="Coming soon...").pack()
    
    def logout(self):
        self.destroy()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


if __name__ == '__main__':
    AdminDashboard()
