# admin_panel.py
# Dark modern sidebar admin panel for JewelMart
# Place this file in: JewelMart/admin/
#
# Requires:
#   - PyQt5
#   - pymongo
#   - database.py (providing get_users_collection, get_products_collection, get_orders_collection)
#
# Features:
#   - Dark sidebar (Home/Products/Orders/Users/Logout)
#   - Dashboard: total counts
#   - Products: add / edit / delete / thumbnails
#   - Orders: view orders, view items, change status
#   - Users: list users, view details, delete
#
from PyQt5 import QtWidgets, QtGui, QtCore
import sys, os, json, shutil
from functools import partial
from database import get_users_collection, get_products_collection, get_orders_collection

# Project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../JewelMart
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CATALOG_PATH = os.path.join(BASE_DIR, "catalog.json")
USERS_JSON = os.path.join(BASE_DIR, "users.json")

# Product statuses / order statuses used in UI
ORDER_STATUSES = ["Pending", "Confirmed", "Packed", "Shipped", "Delivered", "Cancelled"]

# Small helper to ensure assets dir exists
os.makedirs(ASSETS_DIR, exist_ok=True)

# ---------- Small UI helpers ----------
def make_icon(text, size=20):
    """Create a QIcon from text (fallback)."""
    pix = QtGui.QPixmap(size, size)
    pix.fill(QtGui.QColor("transparent"))
    painter = QtGui.QPainter(pix)
    painter.setPen(QtGui.QColor("white"))
    font = painter.font()
    font.setPointSize(10)
    painter.setFont(font)
    painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, text)
    painter.end()
    return QtGui.QIcon(pix)


# ---------- Add / Edit Product Dialog ----------
class ProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Product" + ("" if product is None else " - Edit"))
        self.resize(450, 420)
        self._product = product or {}
        self._image_path = ""
        
        # Light theme stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
            }
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #333333;
            }
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
            QLabel {
                color: #333333;
            }
        """)

        layout = QtWidgets.QFormLayout(self)

        self.name = QtWidgets.QLineEdit(self._product.get("name", ""))
        self.category = QtWidgets.QLineEdit(self._product.get("category", ""))
        self.material = QtWidgets.QLineEdit(self._product.get("material", ""))
        self.price = QtWidgets.QLineEdit(str(self._product.get("price", "")))
        self.desc = QtWidgets.QTextEdit(self._product.get("description", ""))

        image_h = QtWidgets.QHBoxLayout()
        self.img_line = QtWidgets.QLineEdit(self._product.get("image_path", ""))
        self.img_btn = QtWidgets.QPushButton("Choose")
        self.img_btn.clicked.connect(self.choose_image)
        image_h.addWidget(self.img_line)
        image_h.addWidget(self.img_btn)

        layout.addRow("Name:", self.name)
        layout.addRow("Category:", self.category)
        layout.addRow("Material:", self.material)
        layout.addRow("Price:", self.price)
        layout.addRow("Image:", image_h)
        layout.addRow("Description:", self.desc)

        btns = QtWidgets.QHBoxLayout()
        save = QtWidgets.QPushButton("Save")
        cancel = QtWidgets.QPushButton("Cancel")
        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

    def choose_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose product image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self._image_path = path
            self.img_line.setText(path)

    def get_data(self):
        """Return a dict with filled values and image source (if any)."""
        try:
            price_val = float(self.price.text().strip() or 0)
        except Exception:
            price_val = 0
        return {
            "name": self.name.text().strip(),
            "category": self.category.text().strip(),
            "material": self.material.text().strip(),
            "price": price_val,
            "description": self.desc.toPlainText().strip(),
            "image_src": self._image_path or self.img_line.text().strip(),
            "existing_image": self._product.get("image_path", "")
        }


# ---------- Orders Detail Dialog ----------
class OrderDetailDialog(QtWidgets.QDialog):
    def __init__(self, order_doc, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Order {order_doc.get('order_id')}")
        self.resize(700, 480)
        
        # Light theme stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #333333;
                padding: 5px;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
                color: #333333;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                color: #333333;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel(f"<b>Order ID:</b> {order_doc.get('order_id')} &nbsp;&nbsp; <b>User:</b> {order_doc.get('user')} &nbsp;&nbsp; <b>Status:</b> {order_doc.get('status')}")
        header.setStyleSheet("color: #333333; font-size: 12px;")
        layout.addWidget(header)

        self.items_table = QtWidgets.QTableWidget(0, 4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.items_table)

        total_lbl = QtWidgets.QLabel(f"Total: ₹{order_doc.get('total', order_doc.get('total_amount', 0))}")
        total_lbl.setStyleSheet("color: #C8937E; font-weight: bold; font-size: 13px;")
        layout.addWidget(total_lbl)

        # shipping / meta
        meta = QtWidgets.QTextEdit()
        meta.setReadOnly(True)
        meta_text = []
        if order_doc.get("name"):
            meta_text.append(f"Name: {order_doc.get('name')}")
        if order_doc.get("address"):
            meta_text.append("Shipping Address:")
            meta_text.append(order_doc.get("address"))
        meta_text.append("\nRaw summary:")
        for k in ("order_id", "user", "status", "total"):
            meta_text.append(f"{k}: {order_doc.get(k)}")
        meta.setPlainText("\n".join(str(x) for x in meta_text))
        layout.addWidget(meta)

        # populate items
        items = order_doc.get("items", [])
        for it in items:
            r = self.items_table.rowCount()
            self.items_table.insertRow(r)
            self.items_table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(it.get("name", it.get("product_name","")))))
            self.items_table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(it.get("price", 0))))
            self.items_table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(it.get("qty", it.get("quantity", 1)))))
            subtotal = float(it.get("price", 0)) * int(it.get("qty", it.get("quantity", 1)))
            self.items_table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(subtotal)))


# ---------- Main Admin Window ----------
class AdminMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart — Admin Dashboard")
        self.resize(1200, 760)

        # Collections
        self.users_coll = get_users_collection()
        self.products_coll = get_products_collection()
        self.orders_coll = get_orders_collection()

        # Central layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_h = QtWidgets.QHBoxLayout(central)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)

        # Left sidebar (light theme)
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame { background: #F5F5F5; color: #333333; border-right: 1px solid #E0E0E0; }
            QPushButton { 
                background: transparent; 
                color: #666666; 
                border: none; 
                text-align: left; 
                padding: 10px 15px; 
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { 
                background: #EEEEEE; 
                color: #333333;
            }
            QPushButton:checked { 
                background: #F5D7C6; 
                color: #C8937E; 
                font-weight: 700;
                border-left: 4px solid #C8937E;
                padding-left: 11px;
            }
            QLabel#title { 
                color: #C8937E; 
                font-size: 16px; 
                font-weight: 700; 
                padding: 15px; 
            }
        """)
        side_layout = QtWidgets.QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        title = QtWidgets.QLabel("✨ JewelMart Admin")
        title.setObjectName("title")
        side_layout.addWidget(title)
        
        # Divider
        divider = QtWidgets.QFrame()
        divider.setStyleSheet("background-color: #E0E0E0; height: 1px;")
        divider.setMaximumHeight(1)
        side_layout.addWidget(divider)

        # Sidebar buttons
        self.btn_dashboard = QtWidgets.QPushButton("📊 Dashboard")
        self.btn_products = QtWidgets.QPushButton("📦 Products")
        self.btn_orders = QtWidgets.QPushButton("🧾 Orders")
        self.btn_users = QtWidgets.QPushButton("👤 Users")
        self.btn_logout = QtWidgets.QPushButton("🚪 Logout")

        # Make them checkable to show active
        for b in (self.btn_dashboard, self.btn_products, self.btn_orders, self.btn_users):
            b.setCheckable(True)

        # Connect
        self.btn_dashboard.clicked.connect(lambda: self.switch_page("dashboard"))
        self.btn_products.clicked.connect(lambda: self.switch_page("products"))
        self.btn_orders.clicked.connect(lambda: self.switch_page("orders"))
        self.btn_users.clicked.connect(lambda: self.switch_page("users"))
        self.btn_logout.clicked.connect(self.logout)

        # Add buttons to sidebar
        side_layout.addWidget(self.btn_dashboard)
        side_layout.addWidget(self.btn_products)
        side_layout.addWidget(self.btn_orders)
        side_layout.addWidget(self.btn_users)
        side_layout.addStretch()
        side_layout.addWidget(self.btn_logout)

        main_h.addWidget(sidebar)

        # Right area (stacked pages)
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet("background-color: #FAFAFA;")
        main_h.addWidget(self.stack, 1)

        # Pages
        self.page_dashboard = self.make_dashboard_page()
        self.page_products = self.make_products_page()
        self.page_orders = self.make_orders_page()
        self.page_users = self.make_users_page()

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_products)
        self.stack.addWidget(self.page_orders)
        self.stack.addWidget(self.page_users)

        # default
        self.switch_page("dashboard")

    # ------------------------
    # Page: Dashboard
    # ------------------------
    def make_dashboard_page(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("""
            QWidget { background-color: #FAFAFA; }
            QLabel { color: #333333; }
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
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #333333;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:selected {
                background-color: #F5D7C6;
                color: #333333;
            }
        """)
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QtWidgets.QLabel("Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #C8937E;")
        layout.addWidget(header)

        # stats area
        stats_h = QtWidgets.QHBoxLayout()
        self.stat_products = QtWidgets.QLabel("Products: 0")
        self.stat_users = QtWidgets.QLabel("Users: 0")
        self.stat_orders = QtWidgets.QLabel("Orders: 0")
        
        stat_style = """
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 15px;
            font-size: 14px;
            color: #333333;
            font-weight: 500;
        """
        
        for lbl in (self.stat_products, self.stat_users, self.stat_orders):
            lbl.setStyleSheet(stat_style)
            stats_h.addWidget(lbl)
        stats_h.addStretch()
        layout.addLayout(stats_h)

        # recent orders
        recent_label = QtWidgets.QLabel("Recent Orders")
        recent_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; margin-top: 10px;")
        layout.addWidget(recent_label)
        
        self.recent_orders_list = QtWidgets.QListWidget()
        layout.addWidget(self.recent_orders_list, 1)

        refresh_btn = QtWidgets.QPushButton("Refresh Dashboard")
        refresh_btn.clicked.connect(self.load_dashboard)
        layout.addWidget(refresh_btn)

        return w

    def load_dashboard(self):
        try:
            products_count = self.products_coll.count_documents({})
            users_count = self.users_coll.count_documents({})
            orders_count = self.orders_coll.count_documents({})
        except Exception as e:
            products_count = users_count = orders_count = 0

        self.stat_products.setText(f"Products: {products_count}")
        self.stat_users.setText(f"Users: {users_count}")
        self.stat_orders.setText(f"Orders: {orders_count}")

        # recent orders
        self.recent_orders_list.clear()
        try:
            cursor = self.orders_coll.find().sort("_id", -1).limit(10)
            for o in cursor:
                self.recent_orders_list.addItem(f"{o.get('order_id','')} — ₹{o.get('total', o.get('total_amount',''))} — {o.get('status')}")
        except Exception:
            pass

    # ------------------------
    # Page: Products
    # ------------------------
    def make_products_page(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("""
            QWidget { background-color: #FAFAFA; }
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
            }
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
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #333333;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:selected {
                background-color: #F5D7C6;
                color: #333333;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #333333;
            }
            QLabel { color: #333333; }
        """)
        v = QtWidgets.QVBoxLayout(w)
        v.setContentsMargins(20, 20, 20, 20)

        top_h = QtWidgets.QHBoxLayout()
        self.prod_search = QtWidgets.QLineEdit()
        self.prod_search.setPlaceholderText("Search by name or category...")
        self.prod_search.returnPressed.connect(self.load_products)
        btn_search = QtWidgets.QPushButton("Search")
        btn_search.clicked.connect(self.load_products)
        btn_add = QtWidgets.QPushButton("+ Add Product")
        btn_add.clicked.connect(self.add_product)

        top_h.addWidget(self.prod_search)
        top_h.addWidget(btn_search)
        top_h.addWidget(btn_add)
        v.addLayout(top_h)

        # product list area
        self.prod_list_widget = QtWidgets.QListWidget()
        self.prod_list_widget.setIconSize(QtCore.QSize(48, 48))
        self.prod_list_widget.itemClicked.connect(self.on_product_selected)
        v.addWidget(self.prod_list_widget, 1)

        # detail + delete/edit
        bottom_h = QtWidgets.QHBoxLayout()
        self.prod_detail = QtWidgets.QTextEdit(); self.prod_detail.setReadOnly(True)
        bottom_h.addWidget(self.prod_detail, 1)

        right_v = QtWidgets.QVBoxLayout()
        self.btn_edit = QtWidgets.QPushButton("Edit")
        self.btn_edit.clicked.connect(self.edit_product)
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_product)
        right_v.addWidget(self.btn_edit)
        right_v.addWidget(self.btn_delete)
        right_v.addStretch()
        bottom_h.addLayout(right_v)
        v.addLayout(bottom_h)

        # load initially
        self.load_products()

        return w

    def load_products(self):
        self.prod_list_widget.clear()
        q_text = self.prod_search.text().strip().lower()
        q = {}
        if q_text:
            q = {"$or": [{"name": {"$regex": q_text, "$options": "i"}}, {"category": {"$regex": q_text, "$options": "i"}}]}
        try:
            docs = list(self.products_coll.find(q).sort("id", 1))
        except Exception:
            docs = []
        self._products_cache = docs
        for p in docs:
            item = QtWidgets.QListWidgetItem(p.get("name", "(no name)"))
            img = p.get("image_path", "")
            if img:
                path = img if os.path.isabs(img) else os.path.join(ASSETS_DIR, os.path.basename(img))
                if os.path.exists(path):
                    pix = QtGui.QPixmap(path).scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    item.setIcon(QtGui.QIcon(pix))
            self.prod_list_widget.addItem(item)

    def on_product_selected(self, item):
        idx = self.prod_list_widget.row(item)
        if idx < 0 or idx >= len(getattr(self, "_products_cache", [])):
            self.prod_detail.clear()
            return
        p = self._products_cache[idx]
        text = f"ID: {p.get('id')}\nName: {p.get('name')}\nCategory: {p.get('category')}\nMaterial: {p.get('material')}\nPrice: ₹{p.get('price')}\nImage: {p.get('image_path')}\n\nDescription:\n{p.get('description','')}"
        self.prod_detail.setPlainText(text)

    def add_product(self):
        dlg = ProductDialog(self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        data = dlg.get_data()
        # compute new id
        try:
            last = self.products_coll.find_one(sort=[("id", -1)])
            new_id = 1 if last is None else int(last.get("id", 0)) + 1
        except Exception:
            new_id = 1
        img_src = data.get("image_src", "")
        img_name = data.get("existing_image", "")
        if img_src:
            # copy to assets
            try:
                os.makedirs(ASSETS_DIR, exist_ok=True)
                target_name = f"product_{new_id}_" + os.path.basename(img_src)
                target_path = os.path.join(ASSETS_DIR, target_name)
                shutil.copyfile(img_src, target_path)
                img_name = target_name
            except Exception:
                img_name = data.get("existing_image", "")
        # build doc
        doc = {
            "id": new_id,
            "name": data["name"],
            "category": data["category"],
            "material": data["material"],
            "price": data["price"],
            "description": data["description"],
            "image_path": img_name
        }
        try:
            self.products_coll.insert_one(doc)
            QtWidgets.QMessageBox.information(self, "Saved", "Product added.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to add product: {e}")
        self.load_products()

    def edit_product(self):
        sel = self.prod_list_widget.currentRow()
        if sel < 0:
            return
        p = self._products_cache[sel]
        dlg = ProductDialog(self, product=p)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        data = dlg.get_data()
        img_src = data.get("image_src", "")
        img_name = p.get("image_path", "")
        if img_src and os.path.exists(img_src):
            try:
                target_name = f"product_{p.get('id')}_{os.path.basename(img_src)}"
                shutil.copyfile(img_src, os.path.join(ASSETS_DIR, target_name))
                img_name = target_name
            except Exception:
                pass
        update = {
            "name": data["name"],
            "category": data["category"],
            "material": data["material"],
            "price": data["price"],
            "description": data["description"],
            "image_path": img_name
        }
        try:
            self.products_coll.update_one({"id": p.get("id")}, {"$set": update})
            QtWidgets.QMessageBox.information(self, "Saved", "Product updated.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to update product: {e}")
        self.load_products()

    def delete_product(self):
        sel = self.prod_list_widget.currentRow()
        if sel < 0:
            return
        p = self._products_cache[sel]
        ans = QtWidgets.QMessageBox.question(self, "Delete", f"Delete product '{p.get('name')}'?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            return
        try:
            self.products_coll.delete_one({"id": p.get("id")})
            # remove asset file
            img = p.get("image_path", "")
            if img:
                f = os.path.join(ASSETS_DIR, img)
                if os.path.exists(f):
                    os.remove(f)
            QtWidgets.QMessageBox.information(self, "Deleted", "Product removed.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to delete: {e}")
        self.load_products()


    # ------------------------
    # Page: Orders
    # ------------------------
    def make_orders_page(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("""
            QWidget { background-color: #FAFAFA; }
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
            }
            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
            }
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
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #333333;
                padding: 5px;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #F5D7C6;
                color: #333333;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #333333;
            }
            QLabel { color: #333333; }
        """)
        v = QtWidgets.QVBoxLayout(w)
        v.setContentsMargins(20, 20, 20, 20)

        top_h = QtWidgets.QHBoxLayout()
        self.order_search = QtWidgets.QLineEdit()
        self.order_search.setPlaceholderText("Search order id or user email...")
        btn_search = QtWidgets.QPushButton("Search")
        btn_search.clicked.connect(self.load_orders)
        self.order_status_filter = QtWidgets.QComboBox()
        self.order_status_filter.addItem("All")
        self.order_status_filter.addItems(ORDER_STATUSES)
        self.order_status_filter.currentIndexChanged.connect(self.load_orders)
        top_h.addWidget(self.order_search)
        top_h.addWidget(btn_search)
        top_h.addWidget(self.order_status_filter)
        v.addLayout(top_h)

        # Orders table
        self.orders_table = QtWidgets.QTableWidget(0, 6)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "User", "Name", "Total", "Status", "Date"])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.orders_table.itemSelectionChanged.connect(self.on_order_selected)
        v.addWidget(self.orders_table, 1)

        # right area: details + status change
        bottom_h = QtWidgets.QHBoxLayout()
        self.order_items_table = QtWidgets.QTableWidget(0, 4)
        self.order_items_table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal"])
        self.order_items_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        bottom_h.addWidget(self.order_items_table, 1)

        right_v = QtWidgets.QVBoxLayout()
        self.order_info = QtWidgets.QTextEdit(); self.order_info.setReadOnly(True)
        right_v.addWidget(self.order_info)

        status_h = QtWidgets.QHBoxLayout()
        self.order_status_combo = QtWidgets.QComboBox()
        self.order_status_combo.addItems(ORDER_STATUSES)
        status_h.addWidget(QtWidgets.QLabel("Status:"))
        status_h.addWidget(self.order_status_combo)
        save_status_btn = QtWidgets.QPushButton("Save Status")
        save_status_btn.clicked.connect(self.save_order_status)
        status_h.addWidget(save_status_btn)
        right_v.addLayout(status_h)

        quick_ship = QtWidgets.QPushButton("Mark Shipped")
        quick_ship.clicked.connect(lambda: self.quick_set_order_status("Shipped"))
        quick_deliv = QtWidgets.QPushButton("Mark Delivered")
        quick_deliv.clicked.connect(lambda: self.quick_set_order_status("Delivered"))
        right_v.addWidget(quick_ship)
        right_v.addWidget(quick_deliv)
        right_v.addStretch()
        bottom_h.addLayout(right_v)

        v.addLayout(bottom_h)

        # load initially
        self.load_orders()

        return w

    def load_orders(self):
        self.orders_table.setRowCount(0)
        q = {}
        qtext = self.order_search.text().strip()
        if qtext:
            q["$or"] = [{"order_id": {"$regex": qtext, "$options": "i"}}, {"user": {"$regex": qtext, "$options": "i"}}]
        status = self.order_status_filter.currentText()
        if status and status != "All":
            q["status"] = status
        try:
            cursor = list(self.orders_coll.find(q).sort("_id", -1))
        except Exception:
            cursor = []

        self._orders_cache = cursor
        for o in cursor:
            r = self.orders_table.rowCount()
            self.orders_table.insertRow(r)
            self.orders_table.setItem(r, 0, QtWidgets.QTableWidgetItem(o.get("order_id", str(o.get("_id")))))
            self.orders_table.setItem(r, 1, QtWidgets.QTableWidgetItem(o.get("user", "")))
            self.orders_table.setItem(r, 2, QtWidgets.QTableWidgetItem(o.get("name", "")))
            self.orders_table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(o.get("total", o.get("total_amount","")))))
            self.orders_table.setItem(r, 4, QtWidgets.QTableWidgetItem(o.get("status", "")))
            self.orders_table.setItem(r, 5, QtWidgets.QTableWidgetItem(str(o.get("created_at", o.get("date","")))))

    def on_order_selected(self):
        self.order_items_table.setRowCount(0)
        sel = self.orders_table.currentRow()
        if sel < 0:
            self.order_info.clear()
            return
        order_doc = self._orders_cache[sel]
        # populate items
        items = order_doc.get("items", [])
        total_calc = 0
        for it in items:
            r = self.order_items_table.rowCount()
            self.order_items_table.insertRow(r)
            self.order_items_table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(it.get("name", it.get("product_name","")))))
            self.order_items_table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(it.get("price", 0))))
            self.order_items_table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(it.get("qty", it.get("quantity",1)))))
            subtotal = float(it.get("price",0)) * int(it.get("qty", it.get("quantity",1)))
            self.order_items_table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(subtotal)))
            total_calc += subtotal
        # info/meta
        meta_lines = [f"Order ID: {order_doc.get('order_id')}", f"User: {order_doc.get('user')}", f"Name: {order_doc.get('name')}", f"Status: {order_doc.get('status')}", f"Total: ₹{order_doc.get('total', order_doc.get('total_amount',0))}"]
        if order_doc.get("address"):
            meta_lines.append("Shipping Address:")
            meta_lines.append(order_doc.get("address"))
        self.order_info.setPlainText("\n".join(str(x) for x in meta_lines))
        # sync status combo
        st = order_doc.get("status", "")
        try:
            idx = ORDER_STATUSES.index(st)
        except Exception:
            idx = 0
        self.order_status_combo.setCurrentIndex(idx)

    def save_order_status(self):
        sel = self.orders_table.currentRow()
        if sel < 0:
            return
        order_doc = self._orders_cache[sel]
        new_status = self.order_status_combo.currentText()
        try:
            self.orders_coll.update_one({"order_id": order_doc.get("order_id")}, {"$set": {"status": new_status}})
            QtWidgets.QMessageBox.information(self, "Updated", "Order status updated.")
            self.load_orders()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to update: {e}")

    def quick_set_order_status(self, status):
        sel = self.orders_table.currentRow()
        if sel < 0:
            return
        order_doc = self._orders_cache[sel]
        try:
            self.orders_coll.update_one({"order_id": order_doc.get("order_id")}, {"$set": {"status": status}})
            QtWidgets.QMessageBox.information(self, "Updated", f"Order marked {status}.")
            self.load_orders()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed: {e}")

    # ------------------------
    # Page: Users
    # ------------------------
    def make_users_page(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("""
            QWidget { background-color: #FAFAFA; }
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
            }
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
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #333333;
                padding: 5px;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #F5D7C6;
                color: #333333;
            }
            QLabel { color: #333333; }
        """)
        v = QtWidgets.QVBoxLayout(w)
        v.setContentsMargins(20, 20, 20, 20)

        top_h = QtWidgets.QHBoxLayout()
        self.user_search = QtWidgets.QLineEdit()
        self.user_search.setPlaceholderText("Search user by email or name...")
        btn_search = QtWidgets.QPushButton("Search")
        btn_search.clicked.connect(self.load_users)
        top_h.addWidget(self.user_search)
        top_h.addWidget(btn_search)
        v.addLayout(top_h)

        self.users_table = QtWidgets.QTableWidget(0, 4)
        self.users_table.setHorizontalHeaderLabels(["Email", "Name", "Phone", "Actions"])
        self.users_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        v.addWidget(self.users_table)

        self.load_users()
        return w

    def load_users(self):
        self.users_table.setRowCount(0)
        qtext = self.user_search.text().strip()
        q = {}
        if qtext:
            q = {"$or": [{"email": {"$regex": qtext, "$options": "i"}}, {"name": {"$regex": qtext, "$options": "i"}}]}
        try:
            docs = list(self.users_coll.find(q).limit(500))
        except Exception:
            docs = []
        self._users_cache = docs
        for u in docs:
            r = self.users_table.rowCount()
            self.users_table.insertRow(r)
            self.users_table.setItem(r, 0, QtWidgets.QTableWidgetItem(u.get("email","")))
            self.users_table.setItem(r, 1, QtWidgets.QTableWidgetItem(u.get("name","")))
            self.users_table.setItem(r, 2, QtWidgets.QTableWidgetItem(u.get("phone","")))
            btn = QtWidgets.QPushButton("View / Delete")
            btn.clicked.connect(partial(self.user_action, r))
            self.users_table.setCellWidget(r, 3, btn)

    def user_action(self, row):
        u = self._users_cache[row]
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("User Details")
        dlg.resize(420, 320)
        dlg.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                color: #333333;
            }
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
            QLabel { color: #333333; }
        """)
        layout = QtWidgets.QVBoxLayout(dlg)
        layout.addWidget(QtWidgets.QLabel(f"Email: {u.get('email','')}"))
        layout.addWidget(QtWidgets.QLabel(f"Name: {u.get('name','')}"))
        layout.addWidget(QtWidgets.QLabel(f"Phone: {u.get('phone','')}"))
        layout.addWidget(QtWidgets.QLabel("Address:"))
        addr = QtWidgets.QTextEdit()
        addr.setReadOnly(True)
        addr.setPlainText(u.get("address", ""))
        layout.addWidget(addr)
        btn_h = QtWidgets.QHBoxLayout()
        del_btn = QtWidgets.QPushButton("Delete User")
        del_btn.clicked.connect(lambda: self.delete_user(u, dlg))
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_h.addWidget(del_btn)
        btn_h.addStretch()
        btn_h.addWidget(close_btn)
        layout.addLayout(btn_h)
        dlg.exec_()

    def delete_user(self, user_doc, parent_dialog=None):
        ans = QtWidgets.QMessageBox.question(self, "Delete", f"Delete user {user_doc.get('email')}?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            return
        try:
            self.users_coll.delete_one({"email": user_doc.get("email")})
            QtWidgets.QMessageBox.information(self, "Deleted", "User deleted.")
            if parent_dialog:
                parent_dialog.accept()
            self.load_users()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "DB Error", f"Failed to delete user: {e}")

    # ------------------------
    # Switch page / Logout
    # ------------------------
    def switch_page(self, name):
        self.btn_dashboard.setChecked(False)
        self.btn_products.setChecked(False)
        self.btn_orders.setChecked(False)
        self.btn_users.setChecked(False)
        if name == "dashboard":
            self.btn_dashboard.setChecked(True)
            self.stack.setCurrentWidget(self.page_dashboard)
            self.load_dashboard()
        elif name == "products":
            self.btn_products.setChecked(True)
            self.stack.setCurrentWidget(self.page_products)
            self.load_products()
        elif name == "orders":
            self.btn_orders.setChecked(True)
            self.stack.setCurrentWidget(self.page_orders)
            self.load_orders()
        elif name == "users":
            self.btn_users.setChecked(True)
            self.stack.setCurrentWidget(self.page_users)
            self.load_users()

    def logout(self):
        ans = QtWidgets.QMessageBox.question(self, "Logout", "Logout and close admin panel?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            self.close()


# ---------- Run as standalone ----------
def main():
    app = QtWidgets.QApplication(sys.argv)
    try:
        win = AdminMainWindow()
        win.show()
        sys.exit(app.exec_())
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Startup Error", f"Failed to start admin panel: {e}")


if __name__ == "__main__":
    main()

