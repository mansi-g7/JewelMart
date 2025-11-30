
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CATALOG_FILE = os.path.join(BASE_DIR, "catalog.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACKS_FILE = os.path.join(BASE_DIR, "feedbacks.json")
WISHLIST_FILE = os.path.join(BASE_DIR, "wishlist.json")
PAYMENTS_FILE = os.path.join(BASE_DIR, "payments.json")
COUPONS_FILE = os.path.join(BASE_DIR, "coupons.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Utility functions
def load_json(filepath, default=None):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else []

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

class JewelMartAdmin(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💎 JewelMart - Admin Panel")
        self.setGeometry(100, 100, 1200, 700)
        
        # Main widget and layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        self.content_stack = QtWidgets.QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f5f5f0;")
        main_layout.addWidget(self.content_stack)
        
        # Add pages
        self.add_pages()
        
        # Show dashboard by default
        self.content_stack.setCurrentIndex(0)
    
    def create_sidebar(self):
        sidebar = QtWidgets.QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #3d5a4a;
                color: white;
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a6b58;
            }
            QPushButton:pressed {
                background-color: #2d4a3a;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Header
        header = QtWidgets.QLabel("🌿 JewelMart")
        header.setStyleSheet("""
            background-color: #2d4a3a;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
        """)
        layout.addWidget(header)
        
        # Menu items
        menu_items = [
            ("🏠 Dashboard", 0),
            ("💍 Manage Products", 1),
            ("📦 Manage Orders", 2),
            ("👥 Users", 3),
            ("💬 Feedbacks", 4),
            ("❤️ Wishlist", 5),
            ("💳 Payments", 6),
            ("🎟️ Coupons", 7),
            ("⚙️ Admin Settings", 8),
            ("🚪 Logout", 9)
        ]
        
        for text, index in menu_items:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
        
        layout.addStretch()
        return sidebar
    
    def add_pages(self):
        self.content_stack.addWidget(self.create_dashboard())
        self.content_stack.addWidget(self.create_products_page())
        self.content_stack.addWidget(self.create_orders_page())
        self.content_stack.addWidget(self.create_users_page())
        self.content_stack.addWidget(self.create_feedbacks_page())
        self.content_stack.addWidget(self.create_wishlist_page())
        self.content_stack.addWidget(self.create_payments_page())
        self.content_stack.addWidget(self.create_coupons_page())
        self.content_stack.addWidget(self.create_settings_page())
        self.content_stack.addWidget(self.create_logout_page())
    
    def switch_page(self, index):
        if index == 9:  # Logout
            reply = QtWidgets.QMessageBox.question(self, 'Logout', 
                'Are you sure you want to logout?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.close()
        else:
            self.content_stack.setCurrentIndex(index)
    
    def create_page_container(self, title):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d4a3a; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        return widget, layout
    
    def create_dashboard(self):
        widget, layout = self.create_page_container("Dashboard")
        
        # Stats cards
        stats_layout = QtWidgets.QHBoxLayout()
        
        products = load_json(CATALOG_FILE, [])
        users = load_json(USERS_FILE, {})
        orders = load_json(ORDERS_FILE, [])
        
        stats = [
            ("Total Products", len(products), "#4a90e2"),
            ("Total Users", len(users), "#7ed321"),
            ("Total Orders", len(orders), "#f5a623"),
            ("Revenue", f"₹{sum(o.get('total', 0) for o in orders)}", "#bd10e0")
        ]
        
        for title, value, color in stats:
            card = self.create_stat_card(title, str(value), color)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        return widget
    
    def create_stat_card(self, title, value, color):
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 5px;
                padding: 20px;
            }}
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        
        card_layout.addWidget(value_label)
        card_layout.addWidget(title_label)
        
        return card

    
    def create_products_page(self):
        widget, layout = self.create_page_container("Manage Products")
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("➕ Add Product")
        add_btn.clicked.connect(self.add_product)
        add_btn.setStyleSheet("background-color: #3d5a4a; color: white; padding: 10px 20px; border-radius: 5px;")
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Products table
        self.products_table = QtWidgets.QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Material", "Price", "Actions"])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setStyleSheet("background-color: white;")
        layout.addWidget(self.products_table)
        
        self.load_products()
        
        return widget
    
    def load_products(self):
        products = load_json(CATALOG_FILE, [])
        self.products_table.setRowCount(len(products))
        
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(product.get('id', ''))))
            self.products_table.setItem(i, 1, QtWidgets.QTableWidgetItem(product.get('name', '')))
            self.products_table.setItem(i, 2, QtWidgets.QTableWidgetItem(product.get('category', '')))
            self.products_table.setItem(i, 3, QtWidgets.QTableWidgetItem(product.get('material', '')))
            self.products_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"₹{product.get('price', 0)}"))
            
            delete_btn = QtWidgets.QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, idx=i: self.delete_product(idx))
            self.products_table.setCellWidget(i, 5, delete_btn)
    
    def add_product(self):
        dialog = AddProductDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_products()
    
    def delete_product(self, index):
        products = load_json(CATALOG_FILE, [])
        if 0 <= index < len(products):
            reply = QtWidgets.QMessageBox.question(self, 'Delete', 
                f'Delete {products[index].get("name", "this product")}?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                products.pop(index)
                save_json(CATALOG_FILE, products)
                self.load_products()
    
    def create_orders_page(self):
        widget, layout = self.create_page_container("Manage Orders")
        
        self.orders_table = QtWidgets.QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "User", "Date", "Total", "Status"])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setStyleSheet("background-color: white;")
        layout.addWidget(self.orders_table)
        
        orders = load_json(ORDERS_FILE, [])
        self.orders_table.setRowCount(len(orders))
        
        for i, order in enumerate(orders):
            self.orders_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(order.get('id', ''))))
            self.orders_table.setItem(i, 1, QtWidgets.QTableWidgetItem(order.get('user', '')))
            self.orders_table.setItem(i, 2, QtWidgets.QTableWidgetItem(order.get('date', '')))
            self.orders_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"₹{order.get('total', 0)}"))
            self.orders_table.setItem(i, 4, QtWidgets.QTableWidgetItem(order.get('status', 'Pending')))
        
        return widget
    
    def create_users_page(self):
        widget, layout = self.create_page_container("Users")
        
        self.users_table = QtWidgets.QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["Email", "Name", "Joined"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setStyleSheet("background-color: white;")
        layout.addWidget(self.users_table)
        
        users = load_json(USERS_FILE, {})
        self.users_table.setRowCount(len(users))
        
        for i, (email, info) in enumerate(users.items()):
            self.users_table.setItem(i, 0, QtWidgets.QTableWidgetItem(email))
            self.users_table.setItem(i, 1, QtWidgets.QTableWidgetItem(info.get('name', '')))
            self.users_table.setItem(i, 2, QtWidgets.QTableWidgetItem(info.get('joined', '')))
        
        return widget
    
    def create_feedbacks_page(self):
        widget, layout = self.create_page_container("Feedbacks")
        
        self.feedbacks_list = QtWidgets.QListWidget()
        self.feedbacks_list.setStyleSheet("background-color: white; padding: 10px;")
        layout.addWidget(self.feedbacks_list)
        
        feedbacks = load_json(FEEDBACKS_FILE, [])
        for feedback in feedbacks:
            item = f"⭐ {feedback.get('rating', 0)}/5 - {feedback.get('user', 'Anonymous')}: {feedback.get('comment', '')}"
            self.feedbacks_list.addItem(item)
        
        return widget
    
    def create_wishlist_page(self):
        widget, layout = self.create_page_container("Wishlist")
        
        info = QtWidgets.QLabel("View all user wishlists")
        info.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(info)
        
        self.wishlist_table = QtWidgets.QTableWidget()
        self.wishlist_table.setColumnCount(3)
        self.wishlist_table.setHorizontalHeaderLabels(["User", "Product", "Added Date"])
        self.wishlist_table.horizontalHeader().setStretchLastSection(True)
        self.wishlist_table.setStyleSheet("background-color: white;")
        layout.addWidget(self.wishlist_table)
        
        return widget
    
    def create_payments_page(self):
        widget, layout = self.create_page_container("Payments")
        
        self.payments_table = QtWidgets.QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels(["Payment ID", "Order ID", "Amount", "Method", "Status"])
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setStyleSheet("background-color: white;")
        layout.addWidget(self.payments_table)
        
        payments = load_json(PAYMENTS_FILE, [])
        self.payments_table.setRowCount(len(payments))
        
        for i, payment in enumerate(payments):
            self.payments_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(payment.get('id', ''))))
            self.payments_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(payment.get('order_id', ''))))
            self.payments_table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"₹{payment.get('amount', 0)}"))
            self.payments_table.setItem(i, 3, QtWidgets.QTableWidgetItem(payment.get('method', '')))
            self.payments_table.setItem(i, 4, QtWidgets.QTableWidgetItem(payment.get('status', '')))
        
        return widget
    
    def create_coupons_page(self):
        widget, layout = self.create_page_container("Coupons")
        
        btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("➕ Add Coupon")
        add_btn.clicked.connect(self.add_coupon)
        add_btn.setStyleSheet("background-color: #3d5a4a; color: white; padding: 10px 20px; border-radius: 5px;")
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.coupons_table = QtWidgets.QTableWidget()
        self.coupons_table.setColumnCount(4)
        self.coupons_table.setHorizontalHeaderLabels(["Code", "Discount %", "Valid Until", "Actions"])
        self.coupons_table.horizontalHeader().setStretchLastSection(True)
        self.coupons_table.setStyleSheet("background-color: white;")
        layout.addWidget(self.coupons_table)
        
        self.load_coupons()
        
        return widget
    
    def load_coupons(self):
        coupons = load_json(COUPONS_FILE, [])
        self.coupons_table.setRowCount(len(coupons))
        
        for i, coupon in enumerate(coupons):
            self.coupons_table.setItem(i, 0, QtWidgets.QTableWidgetItem(coupon.get('code', '')))
            self.coupons_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{coupon.get('discount', 0)}%"))
            self.coupons_table.setItem(i, 2, QtWidgets.QTableWidgetItem(coupon.get('valid_until', '')))
            
            delete_btn = QtWidgets.QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, idx=i: self.delete_coupon(idx))
            self.coupons_table.setCellWidget(i, 3, delete_btn)
    
    def add_coupon(self):
        dialog = AddCouponDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_coupons()
    
    def delete_coupon(self, index):
        coupons = load_json(COUPONS_FILE, [])
        if 0 <= index < len(coupons):
            coupons.pop(index)
            save_json(COUPONS_FILE, coupons)
            self.load_coupons()
    
    def create_settings_page(self):
        widget, layout = self.create_page_container("Admin Settings")
        
        info = QtWidgets.QLabel("Configure admin panel settings")
        info.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(info)
        
        form = QtWidgets.QFormLayout()
        
        shop_name = QtWidgets.QLineEdit("JewelMart")
        email = QtWidgets.QLineEdit("admin@jewelmart.com")
        phone = QtWidgets.QLineEdit("+91 1234567890")
        
        form.addRow("Shop Name:", shop_name)
        form.addRow("Email:", email)
        form.addRow("Phone:", phone)
        
        save_btn = QtWidgets.QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #3d5a4a; color: white; padding: 10px 20px; border-radius: 5px;")
        form.addRow(save_btn)
        
        layout.addLayout(form)
        layout.addStretch()
        
        return widget
    
    def create_logout_page(self):
        widget = QtWidgets.QWidget()
        return widget


class AddProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Product")
        self.resize(500, 400)
        
        layout = QtWidgets.QFormLayout(self)
        
        self.name = QtWidgets.QLineEdit()
        self.category = QtWidgets.QComboBox()
        self.category.addItems(["Necklace", "Earring", "Nose Pin", "Ring", "Bracelet", "Anklet"])
        self.material = QtWidgets.QLineEdit()
        self.price = QtWidgets.QLineEdit()
        self.description = QtWidgets.QTextEdit()
        self.image_path = QtWidgets.QLineEdit()
        
        image_btn = QtWidgets.QPushButton("Choose Image")
        image_btn.clicked.connect(self.choose_image)
        
        layout.addRow("Name:", self.name)
        layout.addRow("Category:", self.category)
        layout.addRow("Material:", self.material)
        layout.addRow("Price (₹):", self.price)
        layout.addRow("Image:", self.image_path)
        layout.addRow("", image_btn)
        layout.addRow("Description:", self.description)
        
        btn_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        save_btn.clicked.connect(self.save_product)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
    
    def choose_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path.setText(path)
    
    def save_product(self):
        try:
            products = load_json(CATALOG_FILE, [])
            
            new_id = max([p.get('id', 0) for p in products], default=0) + 1
            
            new_product = {
                'id': new_id,
                'name': self.name.text(),
                'category': self.category.currentText(),
                'material': self.material.text(),
                'price': int(self.price.text()),
                'description': self.description.toPlainText(),
                'image_path': self.image_path.text()
            }
            
            products.append(new_product)
            save_json(CATALOG_FILE, products)
            
            QtWidgets.QMessageBox.information(self, "Success", "Product added successfully!")
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to add product: {str(e)}")


class AddCouponDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Coupon")
        self.resize(400, 250)
        
        layout = QtWidgets.QFormLayout(self)
        
        self.code = QtWidgets.QLineEdit()
        self.discount = QtWidgets.QSpinBox()
        self.discount.setRange(1, 100)
        self.discount.setSuffix("%")
        self.valid_until = QtWidgets.QDateEdit()
        self.valid_until.setCalendarPopup(True)
        self.valid_until.setDate(QtCore.QDate.currentDate().addMonths(1))
        
        layout.addRow("Coupon Code:", self.code)
        layout.addRow("Discount:", self.discount)
        layout.addRow("Valid Until:", self.valid_until)
        
        btn_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        save_btn.clicked.connect(self.save_coupon)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
    
    def save_coupon(self):
        coupons = load_json(COUPONS_FILE, [])
        
        new_coupon = {
            'code': self.code.text().upper(),
            'discount': self.discount.value(),
            'valid_until': self.valid_until.date().toString("yyyy-MM-dd")
        }
        
        coupons.append(new_coupon)
        save_json(COUPONS_FILE, coupons)
        
        QtWidgets.QMessageBox.information(self, "Success", "Coupon added successfully!")
        self.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = JewelMartAdmin()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
