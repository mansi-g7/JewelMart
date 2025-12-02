"""Order Management Module - Amazon/Flipkart-like Order Page for JewelMart.

This module provides:
- OrderPage class for displaying all user orders
- Order details view with tracking
- Order status management
- Integration with cart and database
"""

import sys
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from admin.database import get_db
except (ImportError, ModuleNotFoundError):
    def get_db():
        from pymongo import MongoClient
        return MongoClient("mongodb://localhost:27017/")["JewelMart"]


class OrderDetailsDialog(QtWidgets.QDialog):
    """Detailed view of a single order - Amazon/Flipkart style."""
    
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.setWindowTitle(f"Order Details - {order.get('order_id', 'N/A')}")
        self.resize(700, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with order ID and status
        header = QtWidgets.QWidget()
        header.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 15px;")
        header_layout = QtWidgets.QVBoxLayout(header)
        
        order_id_label = QtWidgets.QLabel(f"Order ID: {self.order.get('order_id', 'N/A')}")
        order_id_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        header_layout.addWidget(order_id_label)
        
        date_str = self.format_date(self.order.get('created_at'))
        date_label = QtWidgets.QLabel(f"Order Date: {date_str}")
        date_label.setStyleSheet("color: #666666; font-size: 13px;")
        header_layout.addWidget(date_label)
        
        status = self.order.get('status', 'pending').upper()
        status_label = QtWidgets.QLabel(f"Status: {status}")
        status_color = self.get_status_color(status)
        status_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {status_color};")
        header_layout.addWidget(status_label)
        
        layout.addWidget(header)
        
        # Order tracking timeline
        timeline = self.create_timeline()
        layout.addWidget(timeline)
        
        # Items section
        items_label = QtWidgets.QLabel("Order Items")
        items_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333; margin-top: 10px;")
        layout.addWidget(items_label)
        
        # Items table
        items_table = QtWidgets.QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["Product", "Price", "Quantity", "Subtotal"])
        items_table.horizontalHeader().setStretchLastSection(True)
        items_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        items_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        items_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        items = self.order.get('items', [])
        items_table.setRowCount(len(items))
        
        for idx, item in enumerate(items):
            items_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(item.get('name', '')))
            items_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(f"₹{item.get('price', 0)}"))
            items_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(str(item.get('qty', 1))))
            subtotal = item.get('price', 0) * item.get('qty', 1)
            items_table.setItem(idx, 3, QtWidgets.QTableWidgetItem(f"₹{subtotal}"))
        
        layout.addWidget(items_table)
        
        # Price summary
        summary = self.create_price_summary()
        layout.addWidget(summary)
        
        # Delivery address (if available)
        address = self.order.get('delivery_address')
        if address:
            addr_label = QtWidgets.QLabel("Delivery Address")
            addr_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; margin-top: 10px;")
            layout.addWidget(addr_label)
            
            addr_text = QtWidgets.QTextEdit()
            addr_text.setReadOnly(True)
            addr_text.setMaximumHeight(80)
            addr_text.setText(address)
            layout.addWidget(addr_text)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def create_timeline(self):
        """Create order tracking timeline."""
        timeline_widget = QtWidgets.QWidget()
        timeline_widget.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 15px;")
        timeline_layout = QtWidgets.QVBoxLayout(timeline_widget)
        
        title = QtWidgets.QLabel("Order Tracking")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
        timeline_layout.addWidget(title)
        
        status = self.order.get('status', 'pending').lower()
        
        # Define order stages
        stages = [
            ("Order Placed", "pending"),
            ("Processing", "processing"),
            ("Shipped", "shipped"),
            ("Out for Delivery", "out_for_delivery"),
            ("Delivered", "delivered")
        ]
        
        for stage_name, stage_status in stages:
            stage_widget = self.create_stage_widget(stage_name, stage_status, status)
            timeline_layout.addWidget(stage_widget)
        
        return timeline_widget
    
    def create_stage_widget(self, stage_name, stage_status, current_status):
        """Create a single stage in the timeline."""
        stage = QtWidgets.QWidget()
        stage_layout = QtWidgets.QHBoxLayout(stage)
        stage_layout.setContentsMargins(0, 5, 0, 5)
        
        # Status indicator (circle)
        indicator = QtWidgets.QLabel("●")
        
        # Determine if this stage is completed
        stage_order = ["pending", "processing", "shipped", "out_for_delivery", "delivered"]
        try:
            current_idx = stage_order.index(current_status)
            stage_idx = stage_order.index(stage_status)
            is_completed = stage_idx <= current_idx
        except ValueError:
            is_completed = False
        
        if is_completed:
            indicator.setStyleSheet("color: #4CAF50; font-size: 20px;")
            stage_label = QtWidgets.QLabel(f"✓ {stage_name}")
            stage_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            indicator.setStyleSheet("color: #CCCCCC; font-size: 20px;")
            stage_label = QtWidgets.QLabel(stage_name)
            stage_label.setStyleSheet("color: #999999;")
        
        stage_layout.addWidget(indicator)
        stage_layout.addWidget(stage_label)
        stage_layout.addStretch()
        
        return stage
    
    def create_price_summary(self):
        """Create price breakdown summary."""
        summary_widget = QtWidgets.QWidget()
        summary_widget.setStyleSheet("background-color: #F9F9F9; border-radius: 8px; padding: 15px;")
        summary_layout = QtWidgets.QVBoxLayout(summary_widget)
        
        title = QtWidgets.QLabel("Price Details")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; margin-bottom: 10px;")
        summary_layout.addWidget(title)
        
        total = self.order.get('total', 0)
        
        # Calculate item total
        items_total = sum(item.get('price', 0) * item.get('qty', 1) for item in self.order.get('items', []))
        
        # Price rows
        self.add_price_row(summary_layout, "Items Total", items_total)
        self.add_price_row(summary_layout, "Delivery Charges", 0, is_free=True)
        
        # Divider
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setStyleSheet("background-color: #E0E0E0;")
        summary_layout.addWidget(divider)
        
        # Total amount
        total_layout = QtWidgets.QHBoxLayout()
        total_label = QtWidgets.QLabel("Total Amount")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333333;")
        total_value = QtWidgets.QLabel(f"₹{total}")
        total_value.setStyleSheet("font-size: 16px; font-weight: bold; color: #C8937E;")
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        summary_layout.addLayout(total_layout)
        
        return summary_widget
    
    def add_price_row(self, layout, label, amount, is_free=False):
        """Add a price row to the summary."""
        row = QtWidgets.QHBoxLayout()
        label_widget = QtWidgets.QLabel(label)
        label_widget.setStyleSheet("color: #666666;")
        
        if is_free:
            value_widget = QtWidgets.QLabel("FREE")
            value_widget.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            value_widget = QtWidgets.QLabel(f"₹{amount}")
            value_widget.setStyleSheet("color: #666666;")
        
        row.addWidget(label_widget)
        row.addStretch()
        row.addWidget(value_widget)
        layout.addLayout(row)
    
    def format_date(self, date_obj):
        """Format datetime object to readable string."""
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%d %B %Y, %I:%M %p")
        return "N/A"
    
    def get_status_color(self, status):
        """Get color for order status."""
        status = status.lower()
        colors = {
            'pending': '#FF9800',
            'processing': '#2196F3',
            'shipped': '#9C27B0',
            'out_for_delivery': '#FF5722',
            'delivered': '#4CAF50',
            'cancelled': '#F44336'
        }
        return colors.get(status, '#666666')


class OrderPage(QtWidgets.QWidget):
    """Main order page displaying all user orders - Amazon/Flipkart style."""
    
    def __init__(self, user_id="guest", parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db = get_db()
        self.orders_collection = self.db["order"]
        self.orders = []
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        """Setup the UI layout."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("My Orders")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5D7C6;
                color: #333333;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E8BFB0;
            }
        """)
        refresh_btn.clicked.connect(self.load_orders)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Filter tabs
        self.filter_tabs = QtWidgets.QTabWidget()
        self.filter_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #666666;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #E0E0E0;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #C8937E;
                border-bottom: 2px solid #C8937E;
            }
        """)
        self.filter_tabs.currentChanged.connect(self.filter_orders)
        
        # Create tabs for different order statuses
        self.all_orders_widget = self.create_orders_list_widget()
        self.pending_orders_widget = self.create_orders_list_widget()
        self.shipped_orders_widget = self.create_orders_list_widget()
        self.delivered_orders_widget = self.create_orders_list_widget()
        
        self.filter_tabs.addTab(self.all_orders_widget, "All Orders")
        self.filter_tabs.addTab(self.pending_orders_widget, "Pending")
        self.filter_tabs.addTab(self.shipped_orders_widget, "Shipped")
        self.filter_tabs.addTab(self.delivered_orders_widget, "Delivered")
        
        layout.addWidget(self.filter_tabs)
        
        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(self.status_label)
    
    def create_orders_list_widget(self):
        """Create a scrollable widget for orders list."""
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: white; }")
        
        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        scroll.setWidget(container)
        return scroll
    
    def load_orders(self):
        """Load all orders for the current user from database."""
        try:
            self.orders = list(self.orders_collection.find({"user_id": self.user_id}).sort("created_at", -1))
            self.status_label.setText(f"Loaded {len(self.orders)} orders")
            self.filter_orders()
        except Exception as e:
            print(f"Error loading orders: {e}")
            self.orders = []
            self.status_label.setText("Error loading orders")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load orders: {e}")
    
    def filter_orders(self):
        """Filter orders based on selected tab."""
        current_tab = self.filter_tabs.currentIndex()
        
        if current_tab == 0:  # All orders
            filtered = self.orders
            self.display_orders(self.all_orders_widget, filtered)
        elif current_tab == 1:  # Pending
            filtered = [o for o in self.orders if o.get('status', '').lower() in ['pending', 'processing']]
            self.display_orders(self.pending_orders_widget, filtered)
        elif current_tab == 2:  # Shipped
            filtered = [o for o in self.orders if o.get('status', '').lower() in ['shipped', 'out_for_delivery']]
            self.display_orders(self.shipped_orders_widget, filtered)
        elif current_tab == 3:  # Delivered
            filtered = [o for o in self.orders if o.get('status', '').lower() == 'delivered']
            self.display_orders(self.delivered_orders_widget, filtered)
    
    def display_orders(self, scroll_widget, orders):
        """Display orders in the given scroll widget."""
        # Get the container widget from scroll area
        container = scroll_widget.widget()
        layout = container.layout()
        
        # Clear existing widgets
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not orders:
            no_orders = QtWidgets.QLabel("No orders found")
            no_orders.setStyleSheet("color: #999999; font-size: 14px; padding: 20px;")
            no_orders.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(no_orders)
        else:
            for order in orders:
                order_card = self.create_order_card(order)
                layout.addWidget(order_card)
        
        # Add stretch at the end
        layout.addStretch()
    
    def create_order_card(self, order):
        """Create a card widget for a single order - Amazon/Flipkart style."""
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
            QFrame:hover {
                border: 1px solid #C8937E;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Top row: Order ID, Date, Status
        top_row = QtWidgets.QHBoxLayout()
        
        order_id = QtWidgets.QLabel(f"Order #{order.get('order_id', 'N/A')}")
        order_id.setStyleSheet("font-weight: bold; color: #333333; font-size: 14px;")
        top_row.addWidget(order_id)
        
        top_row.addStretch()
        
        date_str = self.format_date(order.get('created_at'))
        date_label = QtWidgets.QLabel(date_str)
        date_label.setStyleSheet("color: #666666; font-size: 12px;")
        top_row.addWidget(date_label)
        
        layout.addLayout(top_row)
        
        # Status badge
        status = order.get('status', 'pending').upper()
        status_badge = QtWidgets.QLabel(status)
        status_color = self.get_status_color(status)
        status_badge.setStyleSheet(f"""
            background-color: {status_color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        status_badge.setMaximumWidth(120)
        layout.addWidget(status_badge)
        
        # Items summary
        items = order.get('items', [])
        items_count = len(items)
        total_qty = sum(item.get('qty', 1) for item in items)
        
        items_summary = QtWidgets.QLabel(f"{items_count} item(s) • {total_qty} piece(s)")
        items_summary.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(items_summary)
        
        # First few items preview
        preview_layout = QtWidgets.QVBoxLayout()
        for item in items[:3]:  # Show max 3 items
            item_label = QtWidgets.QLabel(f"• {item.get('name', 'Unknown')} (x{item.get('qty', 1)})")
            item_label.setStyleSheet("color: #333333; font-size: 12px;")
            preview_layout.addWidget(item_label)
        
        if len(items) > 3:
            more_label = QtWidgets.QLabel(f"... and {len(items) - 3} more item(s)")
            more_label.setStyleSheet("color: #999999; font-size: 11px; font-style: italic;")
            preview_layout.addWidget(more_label)
        
        layout.addLayout(preview_layout)
        
        # Bottom row: Total and View Details button
        bottom_row = QtWidgets.QHBoxLayout()
        
        total = order.get('total', 0)
        total_label = QtWidgets.QLabel(f"Total: ₹{total}")
        total_label.setStyleSheet("font-weight: bold; color: #C8937E; font-size: 16px;")
        bottom_row.addWidget(total_label)
        
        bottom_row.addStretch()
        
        view_btn = QtWidgets.QPushButton("View Details")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #C8937E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B5845E;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_order_details(order))
        bottom_row.addWidget(view_btn)
        
        layout.addLayout(bottom_row)
        
        return card
    
    def view_order_details(self, order):
        """Open detailed view of an order."""
        dialog = OrderDetailsDialog(order, self)
        dialog.exec_()
    
    def format_date(self, date_obj):
        """Format datetime object to readable string."""
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%d %b %Y")
        return "N/A"
    
    def get_status_color(self, status):
        """Get color for order status."""
        status = status.lower()
        colors = {
            'pending': '#FF9800',
            'processing': '#2196F3',
            'shipped': '#9C27B0',
            'out_for_delivery': '#FF5722',
            'delivered': '#4CAF50',
            'cancelled': '#F44336'
        }
        return colors.get(status, '#666666')


# Standalone test
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("JewelMart - My Orders")
    window.resize(900, 700)
    
    order_page = OrderPage(user_id="guest")
    window.setCentralWidget(order_page)
    window.show()
    
    sys.exit(app.exec_())
