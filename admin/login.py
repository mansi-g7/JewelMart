import tkinter as tk
from tkinter import messagebox
from dashboard import AdminDashboard


# Simple admin credentials (you can change or load from `register` collection later)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"




class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Login")
        self.geometry("420x320")
        self.resizable(False, False)


        tk.Label(self, text="Admin Login", font=("Arial", 20, "bold")).pack(pady=18)


        tk.Label(self, text="Username:").pack()
        self.username = tk.Entry(self)
        self.username.pack(pady=6)


        tk.Label(self, text="Password:").pack()
        self.password = tk.Entry(self, show="*")
        self.password.pack(pady=6)


        tk.Button(self, text="Login", bg="#27ae60", fg="white", width=12,
        command=self.verify_login).pack(pady=18)


    def verify_login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()


        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            messagebox.showinfo("Success", "Login Successful")
            self.destroy()
            AdminDashboard()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")
