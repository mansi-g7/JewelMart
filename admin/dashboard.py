import tkinter as tk
from tkinter import ttk
from database import get_admin_db


# import module openers
from modules.category_page import open_category_window
from modules.jewel_add_page import open_jewel_window
from modules.cart_page import open_cart_window
from modules.order_page import open_order_window
from modules.payment_page import open_payment_window
from modules.bill_page import open_bill_window
from modules.review_page import open_review_window
from modules.register_page import open_register_window




class AdminDashboard(tk.Tk):
def __init__(self):
super().__init__()
self.title("JewelMart — Admin Dashboard")
self.geometry("1200x700")
self.resizable(True, True)


# get admin db (JewelMart -> admin)
self.db = get_admin_db()


self.create_sidebar()
self.create_main_area()


self.mainloop()


def create_sidebar(self):
sidebar = tk.Frame(self, bg="#2c3e50", width=220)
sidebar.pack(side="left", fill="y")


tk.Label(sidebar, text="Admin Panel", bg="#2c3e50", fg="white",
font=("Arial", 18, "bold")).pack(pady=18)


buttons = [
("Category", lambda: open_category_window(self, self.db)),
("Jewel Add", lambda: open_jewel_window(self, self.db)),
("Cart", lambda: open_cart_window(self, self.db)),
("Order", lambda: open_order_window(self, self.db)),
("Payment", lambda: open_payment_window(self, self.db)),
("Bill", lambda: open_bill_window(self, self.db)),
("Review", lambda: open_review_window(self, self.db)),
("Register", lambda: open_register_window(self, self.db)),
]


for text, cmd in buttons:
tk.Button(sidebar, text=text, command=cmd, bg="#34495e", fg="white",
font=("Arial", 12), bd=0, pady=12).pack(fill="x", padx=8, pady=6)


def create_main_area(self):
self.main_frame = tk.Frame(self, bg="#ecf0f1")
self.main_frame.pack(fill="both", expand=True)


# A simple welcome label
tk.Label(self.main_frame, text="Welcome to JewelMart Admin", font=("Arial", 20, "bold"), bg="#ecf0f1").pack(pady=30)
tk.Label(self.main_frame, text="Use the left sidebar to open management windows.", bg="#ecf0f1").pack()