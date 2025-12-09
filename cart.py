"""Shopping Cart Module - Handles cart operations and UI for JewelMart.

This module provides:
- ShoppingCart class for managing cart items with MongoDB persistence
- CartDialog class for displaying and managing cart in a popup window
"""

import uuid
import sys
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from admin.database import get_db
except (ImportError, ModuleNotFoundError):
    def get_db():
        from pymongo import MongoClient
        return MongoClient("mongodb://localhost:27017/")["JewelMart"]


class ShoppingCart:
    """Shopping cart manager with MongoDB persistence."""
    
    def __init__(self, user_id="guest"):
        """Initialize cart for a specific user.
        
        Args:
            user_id: User identifier (email or guest ID). Default is 'guest'.
        """
        self.user_id = user_id
        self.items = []
        self.db = get_db()
        self.cart_collection = self.db["carts"]
        self.load_from_db()
    
    def load_from_db(self):
        """Load cart items from MongoDB for this user."""
        try:
            cart_doc = self.cart_collection.find_one({"user_id": self.user_id})
            if cart_doc:
                self.items = cart_doc.get("items", [])
            else:
                self.items = []
        except Exception as e:
            print(f"Error loading cart from DB: {e}")
            self.items = []
    
    def save_to_db(self):
        """Save cart items to MongoDB for this user."""
        try:
            self.cart_collection.update_one(
                {"user_id": self.user_id},
                {
                    "$set": {
                        "user_id": self.user_id,
                        "items": self.items,
                        "last_updated": datetime.now(),
                        "total": self.get_total(),
                        "item_count": self.get_item_count()
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"Error saving cart to DB: {e}")
    
    def add_item(self, product, qty=1):
        """Add a product to the cart with given quantity. If already exists, increment qty."""
        qty = max(1, int(qty))
        for item in self.items:
            if item.get('id') == product.get('id'):
                item['qty'] = item.get('qty', 0) + qty
                self.save_to_db()
                return item['qty']

        # New item
        self.items.append({
            'id': product.get('id'),
            'name': product.get('name'),
            'price': product.get('price'),
            'qty': qty
        })
        self.save_to_db()
        return qty
    
    def remove_item(self, idx):
        """Remove item at index."""
        if 0 <= idx < len(self.items):
            self.items.pop(idx)
            self.save_to_db()
    
    def update_qty(self, idx, qty):
        """Update quantity of item at index."""
        if 0 <= idx < len(self.items):
            self.items[idx]['qty'] = max(1, qty)
            self.save_to_db()
    
    def get_total(self):
        """Calculate total price."""
        return sum(item.get('price', 0) * item.get('qty', 1) for item in self.items)
    
    def clear(self):
        """Clear all items from cart."""
        self.items.clear()
        self.save_to_db()
    
    def is_empty(self):
        """Check if cart is empty."""
        return len(self.items) == 0
    
    def get_item_count(self):
        """Get total number of items in cart (sum of quantities)."""
        return sum(item.get('qty', 1) for item in self.items)


class DeliveryAddressDialog(QtWidgets.QDialog):
    """Dialog to collect delivery address for order."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delivery Address")
        self.resize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QtWidgets.QLabel("Enter Delivery Address")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Please provide your complete delivery address")
        subtitle.setStyleSheet("color: #666666; font-size: 13px;")
        layout.addWidget(subtitle)
        
        # Address fields
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        form_layout.addRow("Name:", self.name_input)
        
        self.phone_input = QtWidgets.QLineEdit()
        self.phone_input.setPlaceholderText("10-digit mobile number")
        self.phone_input.setMaxLength(10)
        form_layout.addRow("Phone:", self.phone_input)
        
        self.address_input = QtWidgets.QTextEdit()
        self.address_input.setPlaceholderText("House No., Building Name, Street, Area")
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)
        
        self.city_input = QtWidgets.QLineEdit()
        self.city_input.setPlaceholderText("City")
        form_layout.addRow("City:", self.city_input)
        
        self.state_input = QtWidgets.QLineEdit()
        self.state_input.setPlaceholderText("State")
        form_layout.addRow("State:", self.state_input)
        
        self.pincode_input = QtWidgets.QLineEdit()
        self.pincode_input.setPlaceholderText("6-digit PIN code")
        self.pincode_input.setMaxLength(6)
        form_layout.addRow("PIN Code:", self.pincode_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        confirm_btn = QtWidgets.QPushButton("Confirm Address")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #C8937E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B5845E;
            }
        """)
        confirm_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(confirm_btn)
        
        layout.addLayout(button_layout)
    
    def validate_and_accept(self):
        """Validate address fields before accepting."""
        if not self.name_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Required", "Please enter your name")
            return
        
        if not self.phone_input.text().strip() or len(self.phone_input.text().strip()) != 10:
            QtWidgets.QMessageBox.warning(self, "Required", "Please enter a valid 10-digit phone number")
            return
        
        if not self.address_input.toPlainText().strip():
            QtWidgets.QMessageBox.warning(self, "Required", "Please enter your address")
            return
        
        if not self.city_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Required", "Please enter your city")
            return
        
        if not self.state_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Required", "Please enter your state")
            return
        
        if not self.pincode_input.text().strip() or len(self.pincode_input.text().strip()) != 6:
            QtWidgets.QMessageBox.warning(self, "Required", "Please enter a valid 6-digit PIN code")
            return
        
        self.accept()
    
    def get_address(self):
        """Get formatted address string."""
        return f"{self.name_input.text()}\n{self.phone_input.text()}\n{self.address_input.toPlainText()}\n{self.city_input.text()}, {self.state_input.text()} - {self.pincode_input.text()}"


class CartDialog(QtWidgets.QDialog):
    """Shopping cart popup window with quantity edit and checkout."""
    
    def __init__(self, cart, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shopping Cart")
        self.resize(700, 450)
        self.cart = cart  # ShoppingCart instance
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel("🛒 Your Shopping Cart")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #C8937E;")
        layout.addWidget(title)
        
        # Cart table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal", "Action"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Total and buttons
        bottom_layout = QtWidgets.QHBoxLayout()
        
        self.total_label = QtWidgets.QLabel("Total: ₹0")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #C8937E;")
        bottom_layout.addWidget(self.total_label)
        
        bottom_layout.addStretch()
        
        checkout_btn = QtWidgets.QPushButton("Proceed to Checkout")
        checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #C8937E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B5845E;
            }
        """)
        checkout_btn.clicked.connect(self.checkout)
        bottom_layout.addWidget(checkout_btn)
        
        close_btn = QtWidgets.QPushButton("Continue Shopping")
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
        
        # Refresh table with cart items (AFTER total_label is created)
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the cart table with current items."""
        self.table.setRowCount(0)
        
        for idx, item in enumerate(self.cart.items):
            self.table.insertRow(idx)
            
            # Product name
            name_cell = QtWidgets.QTableWidgetItem(item.get('name', ''))
            self.table.setItem(idx, 0, name_cell)
            
            # Price
            price = item.get('price', 0)
            price_cell = QtWidgets.QTableWidgetItem(f"₹{price}")
            self.table.setItem(idx, 1, price_cell)
            
            # Quantity (spinbox)
            qty_spin = QtWidgets.QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(999)
            qty_spin.setValue(item.get('qty', 1))
            qty_spin.valueChanged.connect(lambda val, i=idx: self.update_qty(i, val))
            self.table.setCellWidget(idx, 2, qty_spin)
            
            # Subtotal
            subtotal = price * item.get('qty', 1)
            subtotal_cell = QtWidgets.QTableWidgetItem(f"₹{subtotal}")
            self.table.setItem(idx, 3, subtotal_cell)
            
            # Remove button
            remove_btn = QtWidgets.QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #EE5A52;
                }
            """)
            remove_btn.clicked.connect(lambda checked, i=idx: self.remove_item(i))
            self.table.setCellWidget(idx, 4, remove_btn)
        
        # Update total
        total = self.cart.get_total()
        self.total_label.setText(f"Total: ₹{total}")
    
    def update_qty(self, row, qty):
        """Update quantity for an item."""
        self.cart.update_qty(row, qty)
        self.refresh_table()
    
    def remove_item(self, row):
        """Remove an item from cart with confirmation."""
        if row < len(self.cart.items):
            item_name = self.cart.items[row].get('name', 'Item')
            reply = QtWidgets.QMessageBox.question(self, "Remove Item", 
                f"Remove '{item_name}' from cart?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.cart.remove_item(row)
                self.refresh_table()
    
    def checkout(self):
        """Process checkout and place order with delivery address."""
        if self.cart.is_empty():
            QtWidgets.QMessageBox.warning(self, "Empty Cart", "Your cart is empty!")
            return
        
        total = self.cart.get_total()
        
        # Get delivery address
        address_dialog = DeliveryAddressDialog(self)
        if address_dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        
        delivery_address = address_dialog.get_address()
        if not delivery_address.strip():
            QtWidgets.QMessageBox.warning(self, "Address Required", "Please enter a delivery address!")
            return
        
        # Confirm order
        reply = QtWidgets.QMessageBox.question(self, "Confirm Order", 
            f"Proceed with order for ₹{total}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            order_id = uuid.uuid4().hex[:8].upper()
            
            # Save order to MongoDB
            try:
                db = get_db()
                orders_collection = db["order"]
                order_doc = {
                    "order_id": order_id,
                    "user_id": self.cart.user_id,
                    "items": self.cart.items,
                    "total": total,
                    "status": "pending",
                    "delivery_address": delivery_address,
                    "created_at": datetime.now()
                }
                orders_collection.insert_one(order_doc)
                
                QtWidgets.QMessageBox.information(self, "Order Placed", 
                    f"✓ Thank you for your order!\n\nOrder ID: {order_id}\nTotal: ₹{total}\n\nYour order will be delivered soon!")
                self.cart.clear()
                self.refresh_table()
                self.accept()  # Close cart dialog after successful order
                
            except Exception as e:
                print(f"Error saving order to DB: {e}")
                QtWidgets.QMessageBox.critical(self, "Order Failed", 
                    f"Failed to place order: {e}\n\nPlease try again.")
