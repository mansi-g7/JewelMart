# admin_orders.py
# Place this file inside: JewelMart/admin/
#
# Admin Order Management window (MongoDB)
#
# Features:
#  - List orders (search + filter)
#  - View order items/details
#  - Change status (and save to DB)
#  - Quick actions (Mark Shipped / Delivered)
#
# Usage:
#  from admin_orders import OrdersWindow
#  win = OrdersWindow(get_admin_db())   # pass db returned by your get_admin_db()
#  win.show()

from PyQt5 import QtWidgets, QtCore
import sys
import os
from database import get_admin_db  # your helper that returns admin namespace / db
from bson.objectid import ObjectId

# possible statuses (extend if needed)
STATUSES = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]

class OrdersWindow(QtWidgets.QMainWindow):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin — Order Management")
        self.resize(1000, 640)

        # Accept either a db object or call helper if not provided
        self.db = db or get_admin_db()
        # We assume self.db supports self.db["orders"], self.db["products"] etc.
        self.orders_coll = self.db["orders"]

        # UI layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_h = QtWidgets.QHBoxLayout(central)

        # Left side: search + filter + orders table
        left_frame = QtWidgets.QFrame()
        left_frame.setMinimumWidth(540)
        left_layout = QtWidgets.QVBoxLayout(left_frame)

        search_h = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search by order id or customer email...")
        self.search_edit.returnPressed.connect(self.load_orders)
        search_btn = QtWidgets.QPushButton("Search")
        search_btn.clicked.connect(self.load_orders)
        search_h.addWidget(self.search_edit)
        search_h.addWidget(search_btn)
        left_layout.addLayout(search_h)

        filter_h = QtWidgets.QHBoxLayout()
        filter_h.addWidget(QtWidgets.QLabel("Status:"))
        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItem("All")
        self.status_combo.addItems(STATUSES)
        self.status_combo.currentIndexChanged.connect(self.load_orders)
        filter_h.addWidget(self.status_combo)
        filter_h.addStretch()
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_orders)
        filter_h.addWidget(refresh_btn)
        left_layout.addLayout(filter_h)

        # Orders table
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Order ID", "User", "Name", "Total", "Status", "Date"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_order_selected)
        left_layout.addWidget(self.table)

        main_h.addWidget(left_frame)

        # Right side: order details + status update
        right_frame = QtWidgets.QFrame()
        right_layout = QtWidgets.QVBoxLayout(right_frame)

        self.lbl_order = QtWidgets.QLabel("Select an order to view details")
        self.lbl_order.setWordWrap(True)
        right_layout.addWidget(self.lbl_order)

        # Items table
        self.items_table = QtWidgets.QTableWidget(0, 4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        right_layout.addWidget(self.items_table)

        # Status editor
        status_h = QtWidgets.QHBoxLayout()
        status_h.addWidget(QtWidgets.QLabel("Status:"))
        self.status_edit = QtWidgets.QComboBox()
        self.status_edit.addItems(STATUSES)
        status_h.addWidget(self.status_edit)
        status_h.addStretch()
        save_btn = QtWidgets.QPushButton("Save Status")
        save_btn.clicked.connect(self.save_status)
        status_h.addWidget(save_btn)
        right_layout.addLayout(status_h)

        # Quick action buttons
        quick_h = QtWidgets.QHBoxLayout()
        quick_ship = QtWidgets.QPushButton("Mark Shipped")
        quick_ship.clicked.connect(lambda: self.quick_set_status("Shipped"))
        quick_deliv = QtWidgets.QPushButton("Mark Delivered")
        quick_deliv.clicked.connect(lambda: self.quick_set_status("Delivered"))
        quick_h.addWidget(quick_ship)
        quick_h.addWidget(quick_deliv)
        quick_h.addStretch()
        right_layout.addLayout(quick_h)

        # Order meta (customer details, address if present)
        self.meta_text = QtWidgets.QTextEdit()
        self.meta_text.setReadOnly(True)
        right_layout.addWidget(self.meta_text)

        main_h.addWidget(right_frame, 1)

        # status bar
        self.statusBar().showMessage("Ready")

        # load initial orders
        self.load_orders()

    def load_orders(self):
        """
        Loads orders from MongoDB with optional filtering by search text and status.
        """
        self.table.setRowCount(0)
        search = self.search_edit.text().strip()
        status = self.status_combo.currentText()
        q = {}
        if search:
            # search by order_id or user email (partial)
            q["$or"] = [
                {"order_id": {"$regex": search, "$options": "i"}},
                {"user": {"$regex": search, "$options": "i"}}
            ]
        if status and status != "All":
            q["status"] = status

        try:
            cursor = self.orders_coll.find(q).sort("_id", -1)
            orders = list(cursor)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to load orders:\n{e}")
            return

        for o in orders:
            row = self.table.rowCount()
            self.table.insertRow(row)
            oid = o.get("order_id", str(o.get("_id")))
            user = o.get("user", "")
            name = o.get("name", "")
            total = str(o.get("total", ""))
            st = o.get("status", "")
            date = o.get("created_at", o.get("date", ""))
            # store full order object on the row for quick access
            item_id = QtWidgets.QTableWidgetItem(oid)
            item_id.setData(QtCore.Qt.UserRole, o)
            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(user))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(name))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(total))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(st))
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(str(date)))

        self.statusBar().showMessage(f"{self.table.rowCount()} orders loaded")

    def on_order_selected(self):
        """
        Populate right pane when an order is selected.
        """
        self.items_table.setRowCount(0)
        sel = self.table.currentRow()
        if sel < 0:
            self.lbl_order.setText("Select an order to view details")
            self.meta_text.clear()
            return
        order_item = self.table.item(sel, 0)
        order = order_item.data(QtCore.Qt.UserRole)

        # Show basic header
        header = f"Order ID: {order.get('order_id', '')}\nCustomer: {order.get('user','')} — {order.get('name','')}\nStatus: {order.get('status','')}\nTotal: ₹{order.get('total','')}\n"
        self.lbl_order.setText(header)

        # Items: iterate and populate items_table
        items = order.get("items", [])
        total_calc = 0
        for it in items:
            r = self.items_table.rowCount()
            self.items_table.insertRow(r)
            pname = it.get("name", it.get("product_name", ""))
            price = float(it.get("price", 0) or 0)
            qty = int(it.get("qty", it.get("quantity", 1) or 1))
            subtotal = price * qty
            total_calc += subtotal
            self.items_table.setItem(r, 0, QtWidgets.QTableWidgetItem(pname))
            self.items_table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(price)))
            self.items_table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(qty)))
            self.items_table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(subtotal)))

        # Show metadata / shipping address if present
        meta_lines = []
        if "address" in order:
            meta_lines.append("Shipping Address:")
            meta_lines.append(order.get("address", ""))
            meta_lines.append("")
        # add raw order document view (safe)
        meta_lines.append("Order raw data (summary):")
        for k in ("order_id", "user", "name", "status", "total"):
            meta_lines.append(f"{k}: {order.get(k)}")
        self.meta_text.setPlainText("\n".join(str(x) for x in meta_lines))

        # set status dropdown to current status
        st = order.get("status", "")
        try:
            idx = STATUSES.index(st) if st in STATUSES else 0
        except Exception:
            idx = 0
        self.status_edit.setCurrentIndex(idx)

    def save_status(self):
        """
        Save status selected in status_edit to the DB for the selected order.
        """
        sel = self.table.currentRow()
        if sel < 0:
            return
        order_item = self.table.item(sel, 0)
        order = order_item.data(QtCore.Qt.UserRole)
        new_status = self.status_edit.currentText()
        oid = order.get("_id")
        if oid is None:
            QtWidgets.QMessageBox.warning(self, "Warning", "Selected order has no _id in DB.")
            return
        try:
            self.orders_coll.update_one({"_id": oid}, {"$set": {"status": new_status}})
            QtWidgets.QMessageBox.information(self, "Saved", "Order status updated.")
            self.load_orders()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to update status:\n{e}")

    def quick_set_status(self, status_value):
        """
        Quickly set status for selected order.
        """
        sel = self.table.currentRow()
        if sel < 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select an order first.")
            return
        order_item = self.table.item(sel, 0)
        order = order_item.data(QtCore.Qt.UserRole)
        oid = order.get("_id")
        if oid is None:
            QtWidgets.QMessageBox.warning(self, "Warning", "Selected order has no _id in DB.")
            return
        try:
            self.orders_coll.update_one({"_id": oid}, {"$set": {"status": status_value}})
            QtWidgets.QMessageBox.information(self, "Saved", f"Order marked {status_value}.")
            self.load_orders()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to update status:\n{e}")

# Runable standalone test ----------------------------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    try:
        db = get_admin_db()
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "DB Error", f"Failed to connect to DB: {e}")
        return
    win = OrdersWindow(db)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
