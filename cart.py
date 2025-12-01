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
        """Process checkout and place order."""
        if self.cart.is_empty():
            QtWidgets.QMessageBox.warning(self, "Empty Cart", "Your cart is empty!")
            return
        
        total = self.cart.get_total()
        
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
                    "created_at": datetime.now()
                }
                orders_collection.insert_one(order_doc)
            except Exception as e:
                print(f"Error saving order to DB: {e}")
            
            QtWidgets.QMessageBox.information(self, "Order Placed", 
                f"✓ Thank you for your order!\n\nOrder ID: {order_id}\nTotal: ₹{total}\n\nYour order will be delivered soon!")
            self.cart.clear()
            self.refresh_table()
