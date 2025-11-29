# Jewellery Admin Desktop Application with Full CRUD + Login + MongoDB
# ---------------------------------------------------------------
# This code includes:
# ✔ Admin Login with validation
# ✔ Full CRUD for Jewellery products (Create, Read, Update, Delete)
# ✔ MongoDB Compass connection (pymongo)
# ✔ Fully commented code for easy understanding

import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

# -------------------------------------------------------------
# LOGIN WINDOW CLASS
# -------------------------------------------------------------
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Admin Login")
        self.geometry("400x300")
        self.resizable(False, False)

        # Heading label
        tk.Label(self, text="Admin Login", font=("Arial", 20, "bold")).pack(pady=20)

        # Username input
        tk.Label(self, text="Username:").pack()
        self.username = tk.Entry(self)
        self.username.pack(pady=5)

        # Password input
        tk.Label(self, text="Password:").pack()
        self.password = tk.Entry(self, show="*")
        self.password.pack(pady=5)

        # Login button
        tk.Button(self, text="Login", bg="green", fg="white", command=self.verify_login).pack(pady=20)

    # -----------------------
    # Validate login details
    # -----------------------
    def verify_login(self):
        user = self.username.get()
        pwd = self.password.get()

        # Simple login validation
        if user == "admin" and pwd == "123":
            messagebox.showinfo("Success", "Login Successful")
            self.destroy()
            AdminDashboard()  # Open dashboard
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

# -------------------------------------------------------------
# ADMIN DASHBOARD (CRUD) CLASS
# -------------------------------------------------------------
class AdminDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Jewellery Admin Dashboard")
        self.geometry("1100x600")
        self.resizable(False, False)

        # --------------------------------------
        # CONNECT TO MONGODB
        # --------------------------------------
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client['jewelleryDB']
        self.collection = self.db['products']

        # UI Setup
        self.create_sidebar()
        self.create_table_area()
        self.load_products()

        self.mainloop()

    # -------------------------------------------------
    # SIDEBAR MENU
    # -------------------------------------------------
    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Admin Panel", bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).pack(pady=20)

        # Buttons for CRUD operations
        menu_items = [
            ("Add Product", self.open_add_product),
            ("Update Product", self.open_update_product),
            ("Delete Product", self.delete_product),
            ("Refresh Table", self.load_products)
        ]

        for text, command in menu_items:
            tk.Button(sidebar, text=text, command=command, bg="#34495e", fg="white",
                      font=("Arial", 12), bd=0, pady=10).pack(fill="x", pady=5)

    # -------------------------------------------------
    # TABLE TO DISPLAY PRODUCTS
    # -------------------------------------------------
    def create_table_area(self):
        frame = tk.Frame(self, bg="#ecf0f1")
        frame.pack(fill="both", expand=True)

        columns = ("ID", "Name", "Category", "Price")

        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=200)

        self.table.pack(pady=20)

    # -------------------------------------------------
    # LOAD PRODUCTS FROM DATABASE
    # -------------------------------------------------
    def load_products(self):
        # Clear old rows
        for row in self.table.get_children():
            self.table.delete(row)

        # Insert latest rows
        for product in self.collection.find():
            self.table.insert("", "end", values=(
                str(product['_id']),
                product['name'],
                product['category'],
                product['price']
            ))

    # -------------------------------------------------
    # ADD PRODUCT WINDOW
    # -------------------------------------------------
    def open_add_product(self):
        window = tk.Toplevel(self)
        window.title("Add New Product")
        window.geometry("400x400")

        tk.Label(window, text="Product Name").pack()
        name = tk.Entry(window)
        name.pack()

        tk.Label(window, text="Category").pack()
        category = tk.Entry(window)
        category.pack()

        tk.Label(window, text="Price").pack()
        price = tk.Entry(window)
        price.pack()

        # Save new product
        def save():
            # Insert into MongoDB
            self.collection.insert_one({
                "name": name.get(),
                "category": category.get(),
                "price": price.get()
            })

            messagebox.showinfo("Success", "Product Added")
            window.destroy()
            self.load_products()

        tk.Button(window, text="Save", bg="green", fg="white", command=save).pack(pady=20)

    # -------------------------------------------------
    # UPDATE PRODUCT WINDOW
    # -------------------------------------------------
    def open_update_product(self):
        selected = self.table.focus()

        if not selected:
            messagebox.showwarning("Warning", "Select a product to update")
            return

        values = self.table.item(selected, 'values')
        product_id = values[0]

        window = tk.Toplevel(self)
        window.title("Update Product")
        window.geometry("400x400")

        tk.Label(window, text="Product Name").pack()
        name = tk.Entry(window)
        name.insert(0, values[1])
        name.pack()

        tk.Label(window, text="Category").pack()
        category = tk.Entry(window)
        category.insert(0, values[2])
        category.pack()

        tk.Label(window, text="Price").pack()
        price = tk.Entry(window)
        price.insert(0, values[3])
        price.pack()

        # Update product in MongoDB
        def update():
            self.collection.update_one({'_id': self.collection.find_one({'_id': eval(product_id)})['_id']},
                                       {'$set': {
                                           "name": name.get(),
                                           "category": category.get(),
                                           "price": price.get()
                                       }})
            messagebox.showinfo("Success", "Product Updated")
            window.destroy()
            self.load_products()

        tk.Button(window, text="Update", bg="blue", fg="white", command=update).pack(pady=20)

    # -------------------------------------------------
    # DELETE PRODUCT
    # -------------------------------------------------
    def delete_product(self):
        selected = self.table.focus()

        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete")
            return

        values = self.table.item(selected, 'values')
        product_id = values[0]

        # Confirm delete
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            self.collection.delete_one({'_id': self.collection.find_one({'_id': eval(product_id)})['_id']})
            messagebox.showinfo("Deleted", "Product removed successfully")
            self.load_products()

# -------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------
if __name__ == "__main__":
    LoginWindow().mainloop()