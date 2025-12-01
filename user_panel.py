# # # user_panel.py
# # # Advanced PyQt5 user panel (Amazon-style) — MongoDB-backed
# # #
# # # Place this file in your project's main folder (JewelMart/)
# # # Requires: PyQt5, pymongo, database.get_admin_db()
# # #
# # # Features:
# # #  - Login dialog (users from DB or users.json fallback)
# # #  - Sidebar categories
# # #  - Search + sort
# # #  - Product grid with images
# # #  - Product detail popup
# # #  - Cart window with quantity edit
# # #  - Place order -> saves to orders collection (with username/email)
# # #  - Order history view

# # from PyQt5 import QtWidgets, QtGui, QtCore
# # import sys, os, json, uuid, math
# # from functools import partial
# # from database import get_admin_db

# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../JewelMart
# # ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# # CATALOG_JSON = os.path.join(BASE_DIR, "catalog.json")
# # USERS_JSON = os.path.join(BASE_DIR, "users.json")

# # # Utility functions ---------------------------------------------------------
# # def load_local_catalog():
# #     if not os.path.exists(CATALOG_JSON):
# #         return []
# #     try:
# #         with open(CATALOG_JSON, "r", encoding="utf-8") as f:
# #             return json.load(f)
# #     except Exception:
# #         return []

# # def load_local_users():
# #     if not os.path.exists(USERS_JSON):
# #         return {}
# #     try:
# #         with open(USERS_JSON, "r", encoding="utf-8") as f:
# #             return json.load(f)
# #     except Exception:
# #         return {}

# # # Login dialog --------------------------------------------------------------
# # class LoginDialog(QtWidgets.QDialog):
# #     def __init__(self, db):
# #         super().__init__()
# #         self.db = db
# #         self.user = None
# #         self.setWindowTitle("Login to JewelMart")
# #         self.resize(420, 160)
# #         layout = QtWidgets.QVBoxLayout(self)

# #         form = QtWidgets.QFormLayout()
# #         self.email = QtWidgets.QLineEdit()
# #         self.password = QtWidgets.QLineEdit()
# #         self.password.setEchoMode(QtWidgets.QLineEdit.Password)
# #         form.addRow("Email:", self.email)
# #         form.addRow("Password:", self.password)

# #         layout.addLayout(form)

# #         btns = QtWidgets.QHBoxLayout()
# #         login_btn = QtWidgets.QPushButton("Login")
# #         login_btn.clicked.connect(self.attempt_login)
# #         guest_btn = QtWidgets.QPushButton("Continue as Guest")
# #         guest_btn.clicked.connect(self.continue_guest)
# #         btns.addStretch()
# #         btns.addWidget(guest_btn)
# #         btns.addWidget(login_btn)
# #         layout.addLayout(btns)

# #         self.error_label = QtWidgets.QLabel("")
# #         self.error_label.setStyleSheet("color: red;")
# #         layout.addWidget(self.error_label)

# #     def attempt_login(self):
# #         email = self.email.text().strip().lower()
# #         pw = self.password.text().strip()
# #         if not email:
# #             self.error_label.setText("Enter an email.")
# #             return

# #         # try DB users
# #         try:
# #             users = list(self.db["users"].find({"email": email}))
# #             if users:
# #                 # naive plaintext password check if 'password' field exists
# #                 u = users[0]
# #                 if "password" not in u or u["password"] == pw:
# #                     self.user = {"email": email, "name": u.get("name", ""), "_id": u.get("_id")}
# #                     self.accept()
# #                     return
# #                 else:
# #                     self.error_label.setText("Invalid password.")
# #                     return
# #         except Exception:
# #             pass

# #         # fallback local users.json
# #         local = load_local_users()
# #         if email in local:
# #             if local[email].get("password", "") == pw or local[email].get("password", "") == "":
# #                 self.user = {"email": email, "name": local[email].get("name", "")}
# #                 self.accept()
# #                 return
# #             else:
# #                 self.error_label.setText("Invalid password.")
# #                 return

# #         # not found
# #         self.error_label.setText("User not found. Use guest or register via admin.")

# #     def continue_guest(self):
# #         self.user = {"email": "guest", "name": "Guest"}
# #         self.accept()

# # # Product card widget -------------------------------------------------------
# # class ProductCard(QtWidgets.QFrame):
# #     add_to_cart = QtCore.pyqtSignal(dict)  # emits product dict

# #     def __init__(self, product):
# #         super().__init__()
# #         self.product = product
# #         self.setFrameShape(QtWidgets.QFrame.StyledPanel)
# #         self.setFixedSize(260, 240)
# #         self.init_ui()

# #     def init_ui(self):
# #         v = QtWidgets.QVBoxLayout(self)
# #         v.setContentsMargins(6,6,6,6)
# #         # image
# #         self.img_lb = QtWidgets.QLabel()
# #         self.img_lb.setFixedHeight(120)
# #         self.img_lb.setAlignment(QtCore.Qt.AlignCenter)
# #         img = self.product.get("image_path", "")
# #         if img:
# #             p = img if os.path.isabs(img) else os.path.join(ASSETS_DIR, os.path.basename(img))
# #             if os.path.exists(p):
# #                 pix = QtGui.QPixmap(p).scaled(220, 120, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
# #                 self.img_lb.setPixmap(pix)
# #             else:
# #                 self.img_lb.setText("No Image")
# #         else:
# #             self.img_lb.setText("No Image")
# #         v.addWidget(self.img_lb)

# #         # title & category
# #         title = QtWidgets.QLabel(self.product.get("name", "(no name)"))
# #         title.setWordWrap(True)
# #         title.setStyleSheet("font-weight:600;")
# #         v.addWidget(title)

# #         meta = QtWidgets.QLabel(f"{self.product.get('category','')} — {self.product.get('material','')}")
# #         meta.setStyleSheet("color: gray; font-size: 11px;")
# #         v.addWidget(meta)

# #         # price + buttons
# #         h = QtWidgets.QHBoxLayout()
# #         price = QtWidgets.QLabel(f"₹{self.product.get('price',0)}")
# #         h.addWidget(price)
# #         h.addStretch()
# #         view_btn = QtWidgets.QPushButton("View")
# #         view_btn.clicked.connect(self.show_detail)
# #         cart_btn = QtWidgets.QPushButton("Add")
# #         cart_btn.clicked.connect(self.do_add)
# #         h.addWidget(view_btn)
# #         h.addWidget(cart_btn)
# #         v.addLayout(h)

# #     def show_detail(self):
# #         dlg = ProductDetailDialog(self.product)
# #         dlg.exec_()

# #     def do_add(self):
# #         self.add_to_cart.emit(self.product)

# # # Product detail dialog -----------------------------------------------------
# # class ProductDetailDialog(QtWidgets.QDialog):
# #     def __init__(self, product):
# #         super().__init__()
# #         self.product = product
# #         self.setWindowTitle(product.get("name", "Product"))
# #         self.resize(560, 420)
# #         layout = QtWidgets.QHBoxLayout(self)

# #         # image left
# #         left = QtWidgets.QVBoxLayout()
# #         img_lb = QtWidgets.QLabel()
# #         img_lb.setAlignment(QtCore.Qt.AlignCenter)
# #         img_lb.setFixedWidth(260)
# #         img = product.get("image_path", "")
# #         if img:
# #             p = img if os.path.isabs(img) else os.path.join(ASSETS_DIR, os.path.basename(img))
# #             if os.path.exists(p):
# #                 pix = QtGui.QPixmap(p).scaled(250, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
# #                 img_lb.setPixmap(pix)
# #             else:
# #                 img_lb.setText("No image")
# #         else:
# #             img_lb.setText("No image")
# #         left.addWidget(img_lb)
# #         layout.addLayout(left)

# #         # right details
# #         r = QtWidgets.QVBoxLayout()
# #         name = QtWidgets.QLabel(product.get("name", ""))
# #         name.setStyleSheet("font-size:18px; font-weight:700;")
# #         r.addWidget(name)
# #         r.addWidget(QtWidgets.QLabel(f"Category: {product.get('category','')}"))
# #         r.addWidget(QtWidgets.QLabel(f"Material: {product.get('material','')}"))
# #         r.addWidget(QtWidgets.QLabel(f"Price: ₹{product.get('price',0)}"))
# #         r.addWidget(QtWidgets.QLabel(f"Product ID: {product.get('id')}"))
# #         r.addSpacing(12)
# #         desc = QtWidgets.QTextEdit()
# #         desc.setReadOnly(True)
# #         desc.setPlainText(product.get("description",""))
# #         desc.setFixedHeight(180)
# #         r.addWidget(desc)

# #         btn_h = QtWidgets.QHBoxLayout()
# #         self.qty_spin = QtWidgets.QSpinBox(); self.qty_spin.setMinimum(1); self.qty_spin.setMaximum(999)
# #         add_btn = QtWidgets.QPushButton("Add to Cart")
# #         add_btn.clicked.connect(self.add_and_close)
# #         btn_h.addWidget(QtWidgets.QLabel("Qty:"))
# #         btn_h.addWidget(self.qty_spin)
# #         btn_h.addStretch()
# #         btn_h.addWidget(add_btn)
# #         r.addLayout(btn_h)

# #         layout.addLayout(r)

# #     def add_and_close(self):
# #         qty = self.qty_spin.value()
# #         # return product + qty by setting attribute
# #         self.product["_selected_qty"] = qty
# #         self.accept()

# # # Cart dialog ----------------------------------------------------------------
# # class CartDialog(QtWidgets.QDialog):
# #     def __init__(self, parent, cart_items, db, user):
# #         super().__init__(parent)
# #         self.cart = cart_items  # list of dict (with keys id, name, price, qty)
# #         self.db = db
# #         self.user = user
# #         self.setWindowTitle("Your Cart")
# #         self.resize(620, 420)
# #         layout = QtWidgets.QVBoxLayout(self)

# #         self.table = QtWidgets.QTableWidget(0, 5)
# #         self.table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Subtotal", ""])
# #         self.table.horizontalHeader().setStretchLastSection(False)
# #         self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
# #         layout.addWidget(self.table)

# #         btn_h = QtWidgets.QHBoxLayout()
# #         self.total_label = QtWidgets.QLabel("Total: ₹0")
# #         btn_h.addWidget(self.total_label)
# #         btn_h.addStretch()
# #         remove_btn = QtWidgets.QPushButton("Remove Selected")
# #         remove_btn.clicked.connect(self.remove_selected)
# #         btn_h.addWidget(remove_btn)
# #         checkout_btn = QtWidgets.QPushButton("Place Order")
# #         checkout_btn.clicked.connect(self.place_order)
# #         btn_h.addWidget(checkout_btn)
# #         layout.addLayout(btn_h)

# #         self.refresh_table()

# #     def refresh_table(self):
# #         self.table.setRowCount(0)
# #         total = 0
# #         for item in self.cart:
# #             row = self.table.rowCount()
# #             self.table.insertRow(row)
# #             self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("name","")))
# #             self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item.get("price",0))))
# #             qty_w = QtWidgets.QSpinBox(); qty_w.setMinimum(1); qty_w.setValue(item.get("qty",1))
# #             qty_w.valueChanged.connect(partial(self.on_qty_changed, row))
# #             self.table.setCellWidget(row, 2, qty_w)
# #             subtotal = item.get("price",0) * item.get("qty",1)
# #             self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(subtotal)))
# #             self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item.get("id"))))
# #             total += subtotal
# #         self.total_label.setText(f"Total: ₹{total}")

# #     def on_qty_changed(self, row, val):
# #         # update cart and subtotal cell
# #         item = self.cart[row]
# #         item["qty"] = val
# #         subtotal = item.get("price",0) * val
# #         self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(subtotal)))
# #         # recalc total
# #         total = sum(it.get("price",0) * it.get("qty",1) for it in self.cart)
# #         self.total_label.setText(f"Total: ₹{total}")

# #     def remove_selected(self):
# #         row = self.table.currentRow()
# #         if row < 0:
# #             return
# #         self.cart.pop(row)
# #         self.refresh_table()

# #     def place_order(self):
# #         if not self.cart:
# #             QtWidgets.QMessageBox.warning(self, "Empty", "Cart is empty.")
# #             return
# #         total = sum(it.get("price",0) * it.get("qty",1) for it in self.cart)
# #         ok = QtWidgets.QMessageBox.question(self, "Confirm Order", f"Place order for ₹{total}?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
# #         if ok != QtWidgets.QMessageBox.Yes:
# #             return

# #         # build order doc
# #         order = {
# #             "order_id": str(uuid.uuid4()),
# #             "user": self.user.get("email","guest"),
# #             "name": self.user.get("name","Guest"),
# #             "items": [{"product_id": it.get("id"), "name": it.get("name"), "price": it.get("price"), "qty": it.get("qty",1)} for it in self.cart],
# #             "total": total,
# #             "status": "Pending"
# #         }

# #         try:
# #             self.db["orders"].insert_one(order)
# #         except Exception as e:
# #             QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save order: {e}")
# #             return

# #         # Optionally decrement stock if product documents have 'stock'
# #         for it in self.cart:
# #             try:
# #                 self.db["products"].update_one({"id": it.get("id")}, {"$inc": {"stock": -int(it.get("qty",1))}})
# #             except Exception:
# #                 pass

# #         QtWidgets.QMessageBox.information(self, "Success", f"Order placed. ID: {order['order_id']}")
# #         self.cart.clear()
# #         self.accept()

# # # Main application window ---------------------------------------------------
# # class UserWindow(QtWidgets.QMainWindow):
# #     def __init__(self, db, user):
# #         super().__init__()
# #         self.db = db
# #         self.user = user
# #         self.setWindowTitle(f"JewelMart — Welcome {user.get('name','Guest')}")
# #         self.resize(1200, 760)

# #         # main layout: left sidebar, right main area
# #         central = QtWidgets.QWidget()
# #         self.setCentralWidget(central)
# #         h = QtWidgets.QHBoxLayout(central)

# #         # Sidebar
# #         sidebar = QtWidgets.QFrame()
# #         sidebar.setFixedWidth(260)
# #         s_layout = QtWidgets.QVBoxLayout(sidebar)
# #         s_layout.setContentsMargins(8,8,8,8)

# #         # Search
# #         self.search = QtWidgets.QLineEdit()
# #         self.search.setPlaceholderText("Search products...")
# #         self.search.textChanged.connect(self.on_search)
# #         s_layout.addWidget(self.search)

# #         # Category list
# #         s_layout.addWidget(QtWidgets.QLabel("Categories"))
# #         self.cat_list = QtWidgets.QListWidget()
# #         self.cat_list.itemClicked.connect(self.on_category_selected)
# #         s_layout.addWidget(self.cat_list)

# #         # Sort options
# #         s_layout.addWidget(QtWidgets.QLabel("Sort by"))
# #         self.sort_combo = QtWidgets.QComboBox()
# #         self.sort_combo.addItems(["Default", "Price: Low → High", "Price: High → Low", "Name A→Z"])
# #         self.sort_combo.currentIndexChanged.connect(self.render_products)
# #         s_layout.addWidget(self.sort_combo)

# #         # Cart & Orders buttons
# #         btn_cart = QtWidgets.QPushButton("View Cart")
# #         btn_cart.clicked.connect(self.open_cart)
# #         s_layout.addWidget(btn_cart)

# #         btn_orders = QtWidgets.QPushButton("My Orders")
# #         btn_orders.clicked.connect(self.show_orders)
# #         s_layout.addWidget(btn_orders)

# #         s_layout.addStretch()
# #         h.addWidget(sidebar)

# #         # Right area: products grid in scroll
# #         right = QtWidgets.QWidget()
# #         r_layout = QtWidgets.QVBoxLayout(right)

# #         self.grid_scroll = QtWidgets.QScrollArea()
# #         self.grid_scroll.setWidgetResizable(True)
# #         self.grid_container = QtWidgets.QWidget()
# #         self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
# #         self.grid_layout.setSpacing(14)
# #         self.grid_layout.setContentsMargins(12,12,12,12)
# #         self.grid_scroll.setWidget(self.grid_container)
# #         r_layout.addWidget(self.grid_scroll)

# #         # status bar
# #         self.status_label = QtWidgets.QLabel("")
# #         r_layout.addWidget(self.status_label)

# #         h.addWidget(right, 1)

# #         # data
# #         self.products = []
# #         self.filtered_products = []
# #         self.cart = []  # list of dicts: {id,name,price,qty}

# #         # load categories & products
# #         self.load_categories()
# #         self.load_products()
# #         self.render_products()

# #     def load_categories(self):
# #         cats = []
# #         try:
# #             # distinct categories from DB
# #             cats = self.db["products"].distinct("category")
# #         except Exception:
# #             # fallback: build from local catalog
# #             local = load_local_catalog()
# #             cats = sorted({p.get("category","") for p in local})
# #         self.cat_list.clear()
# #         self.cat_list.addItem("All")
# #         for c in sorted([c for c in cats if c]):
# #             self.cat_list.addItem(c)

# #     def load_products(self):
# #         try:
# #             self.products = list(self.db["products"].find())
# #         except Exception:
# #             self.products = load_local_catalog()
# #         self.filtered_products = list(self.products)
# #         self.status_label.setText(f"{len(self.products)} products loaded")

# #     def on_search(self, text):
# #         text = text.strip().lower()
# #         if not text:
# #             self.filtered_products = list(self.products)
# #         else:
# #             self.filtered_products = [p for p in self.products if text in (p.get("name","")+" "+p.get("category","")).lower()]
# #         self.render_products()

# #     def on_category_selected(self, item):
# #         cat = item.text()
# #         if cat == "All":
# #             self.filtered_products = list(self.products)
# #         else:
# #             self.filtered_products = [p for p in self.products if p.get("category","") == cat]
# #         self.render_products()

# #     def sort_products(self, items):
# #         idx = self.sort_combo.currentIndex()
# #         if idx == 1:  # Price Low -> High
# #             return sorted(items, key=lambda x: float(x.get("price",0) or 0))
# #         if idx == 2:  # Price High -> Low
# #             return sorted(items, key=lambda x: float(x.get("price",0) or 0), reverse=True)
# #         if idx == 3:  # Name
# #             return sorted(items, key=lambda x: x.get("name","").lower())
# #         return items

# #     def render_products(self):
# #         # clear grid
# #         while self.grid_layout.count():
# #             it = self.grid_layout.takeAt(0)
# #             w = it.widget()
# #             if w:
# #                 w.deleteLater()

# #         items = self.sort_products(self.filtered_products)
# #         cols = 3
# #         r = c = 0
# #         for p in items:
# #             card = ProductCard(p)
# #             card.add_to_cart.connect(self.add_cart_item)
# #             self.grid_layout.addWidget(card, r, c)
# #             c += 1
# #             if c >= cols:
# #                 c = 0; r += 1

# #     def add_cart_item(self, product):
# #         # if detail qty set (from ProductDetailDialog), use it
# #         qty = int(product.pop("_selected_qty", 1))
# #         # check if already in cart
# #         for it in self.cart:
# #             if it.get("id") == product.get("id"):
# #                 it["qty"] += qty
# #                 break
# #         else:
# #             self.cart.append({"id": product.get("id"), "name": product.get("name"), "price": int(product.get("price",0)), "qty": qty})
# #         QtWidgets.QMessageBox.information(self, "Cart", f"Added {product.get('name')} x{qty} to cart.")

# #     def open_cart(self):
# #         dlg = CartDialog(self, self.cart, self.db, self.user)
# #         dlg.exec_()
# #         # refresh after possible order placement (cart cleared)
# #         self.cart = [it for it in self.cart if it.get("qty",0) > 0]
# #         self.status_label.setText(f"Cart: {len(self.cart)} items")

# #     def show_orders(self):
# #         # list orders for this user (by email)
# #         user_email = self.user.get("email", "guest")
# #         try:
# #             orders = list(self.db["orders"].find({"user": user_email}).sort("_id", -1))
# #         except Exception:
# #             orders = []
# #         dlg = QtWidgets.QDialog(self)
# #         dlg.setWindowTitle("My Orders")
# #         dlg.resize(700, 420)
# #         layout = QtWidgets.QVBoxLayout(dlg)
# #         lw = QtWidgets.QListWidget()
# #         for o in orders:
# #             lw.addItem(f"{o.get('order_id')} — ₹{o.get('total')} — {o.get('status')}")
# #         layout.addWidget(lw)
# #         btn = QtWidgets.QPushButton("Close")
# #         btn.clicked.connect(dlg.accept)
# #         layout.addWidget(btn)
# #         dlg.exec_()

# # # Application entry ---------------------------------------------------------
# # def main():
# #     # Connect to admin DB namespace (same helper used by admin)
# #     try:
# #         db = get_admin_db()
# #     except Exception as e:
# #         # fallback: try to create a minimal compatible object that raises on write
# #         QtWidgets.QMessageBox.critical(None, "DB Error", f"Failed to connect to DB: {e}")
# #         return

# #     # Login
# #     login = LoginDialog(db)
# #     if login.exec_() != QtWidgets.QDialog.Accepted:
# #         return
# #     user = login.user or {"email":"guest","name":"Guest"}

# #     app = QtWidgets.QApplication(sys.argv)
# #     win = UserWindow(db, user)
# #     win.show()
# #     sys.exit(app.exec_())

# # if __name__ == "__main__":
# #     main()


# # user_panel.py
# from PyQt5 import QtWidgets, QtGui, QtCore
# import sys, os
# from pymongo import MongoClient

# # -----------------------
# #  MONGODB CONNECTION
# # -----------------------
# try:
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["JewelMart"]
#     product_col = db["jewel_add"]
#     print("Connected to MongoDB")
# except Exception as e:
#     print("ERROR:", e)


# # -----------------------
# #  PROJECT IMAGE PATH
# # -----------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)
# ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")



# # -----------------------
# # PRODUCT DETAILS POPUP
# # -----------------------
# class ProductDetails(QtWidgets.QDialog):
#     def __init__(self, product, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Product Details")
#         self.resize(400, 450)

#         layout = QtWidgets.QVBoxLayout(self)

#         # Image
#         img_lbl = QtWidgets.QLabel()
#         img_lbl.setAlignment(QtCore.Qt.AlignCenter)
#         img_lbl.setFixedHeight(200)

#         img_name = product.get("image_path", "")
#         img_full = os.path.join(ASSETS_DIR, img_name)

#         if img_name and os.path.exists(img_full):
#             pix = QtGui.QPixmap(img_full).scaled(300, 200, QtCore.Qt.KeepAspectRatio)
#             img_lbl.setPixmap(pix)
#         else:
#             img_lbl.setText("No image")

#         layout.addWidget(img_lbl)

#         # Text details
#         layout.addWidget(QtWidgets.QLabel(f"<b>Name:</b> {product.get('name','')}"))
#         layout.addWidget(QtWidgets.QLabel(f"<b>Category:</b> {product.get('category','')}"))
#         layout.addWidget(QtWidgets.QLabel(f"<b>Material:</b> {product.get('material','')}"))
#         layout.addWidget(QtWidgets.QLabel(f"<b>Price:</b> ₹{product.get('price',0)}"))

#         desc = QtWidgets.QTextEdit()
#         desc.setReadOnly(True)
#         desc.setText(product.get("description", "No description"))
#         layout.addWidget(QtWidgets.QLabel("<b>Description:</b>"))
#         layout.addWidget(desc)

#         close_btn = QtWidgets.QPushButton("Close")
#         close_btn.clicked.connect(self.close)
#         layout.addWidget(close_btn)



# # -----------------------
# # MAIN USER PANEL WINDOW
# # -----------------------
# class UserPanel(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("JewelMart — User Panel")
#         self.resize(900, 600)

#         central = QtWidgets.QWidget()
#         self.setCentralWidget(central)
#         v = QtWidgets.QVBoxLayout(central)

#         # Search bar
#         top = QtWidgets.QHBoxLayout()
#         self.search = QtWidgets.QLineEdit()
#         self.search.setPlaceholderText("Search by product name or category...")
#         search_btn = QtWidgets.QPushButton("Search")
#         search_btn.clicked.connect(self.search_products)

#         refresh_btn = QtWidgets.QPushButton("Refresh")
#         refresh_btn.clicked.connect(self.load_products)

#         top.addWidget(self.search)
#         top.addWidget(search_btn)
#         top.addWidget(refresh_btn)
#         v.addLayout(top)

#         # Scroll Area
#         self.scroll = QtWidgets.QScrollArea()
#         self.scroll.setWidgetResizable(True)

#         self.grid_container = QtWidgets.QWidget()
#         self.grid = QtWidgets.QGridLayout(self.grid_container)
#         self.grid.setSpacing(15)

#         self.scroll.setWidget(self.grid_container)
#         v.addWidget(self.scroll)

#         self.status = QtWidgets.QLabel("")
#         v.addWidget(self.status)

#         self.products = []
#         self.load_products()


#     # -------- GRID CLEAR ----------
#     def clear_grid(self):
#         while self.grid.count():
#             item = self.grid.takeAt(0)
#             w = item.widget()
#             if w:
#                 w.deleteLater()

#     # -------- LOAD PRODUCTS ----------
#     def load_products(self):
#         self.products = list(product_col.find())
#         self.render_products(self.products)
#         self.status.setText(f"Loaded {len(self.products)} products")

#     # -------- SEARCH ----------
#     def search_products(self):
#         text = self.search.text().strip().lower()
#         if not text:
#             self.load_products()
#             return

#         results = []
#         for p in self.products:
#             if (text in p.get("name","").lower()) or (text in p.get("category","").lower()):
#                 results.append(p)

#         self.render_products(results)
#         self.status.setText(f"Found {len(results)} products")

#     # -------- RENDER PRODUCTS ----------
#     def render_products(self, products):
#         self.clear_grid()

#         row = col = 0
#         for p in products:
#             card = self.make_card(p)
#             self.grid.addWidget(card, row, col)
#             col += 1
#             if col >= 3:
#                 row += 1
#                 col = 0

#     # -------- PRODUCT CARD ----------
#     def make_card(self, p):
#         frame = QtWidgets.QFrame()
#         frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
#         frame.setFixedSize(260, 210)

#         layout = QtWidgets.QVBoxLayout(frame)

#         # Image
#         img = QtWidgets.QLabel()
#         img.setFixedHeight(110)
#         img.setAlignment(QtCore.Qt.AlignCenter)

#         img_name = p.get("image_path", "")
#         img_full = os.path.join(ASSETS_DIR, img_name)

#         if img_name and os.path.exists(img_full):
#             pix = QtGui.QPixmap(img_full).scaled(220, 110, QtCore.Qt.KeepAspectRatio)
#             img.setPixmap(pix)
#         else:
#             img.setText("No image")

#         layout.addWidget(img)

#         # Name
#         layout.addWidget(QtWidgets.QLabel(f"<b>{p.get('name','')}</b>"))
#         layout.addWidget(QtWidgets.QLabel(f"{p.get('category')} | {p.get('material')}"))

#         bottom = QtWidgets.QHBoxLayout()
#         bottom.addWidget(QtWidgets.QLabel(f"₹{p.get('price',0)}"))

#         view_btn = QtWidgets.QPushButton("View")
#         view_btn.clicked.connect(lambda: self.open_details(p))
#         bottom.addWidget(view_btn)

#         layout.addLayout(bottom)

#         return frame


#     # -------- OPEN DETAILS ----------
#     def open_details(self, product):
#         dlg = ProductDetails(product, self)
#         dlg.exec_()



# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     ui = UserPanel()
#     ui.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()

# user_panel.py
from PyQt5 import QtWidgets, QtGui, QtCore
import sys, os
from pymongo import MongoClient
from cart import ShoppingCart, CartDialog

# -----------------------
#  MONGODB CONNECTION
# -----------------------
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["JewelMart"]
    product_col = db["jewel_add"]
    print("Connected to MongoDB")
except Exception as e:
    print("ERROR:", e)


# -----------------------
#  PROJECT IMAGE PATH
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")



# -----------------------
# SHOPPING CART DIALOG
# -----------------------

# -----------------------
# PRODUCT DETAILS POPUP
# -----------------------
class ProductDetails(QtWidgets.QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Product Details")
        self.resize(400, 450)

        layout = QtWidgets.QVBoxLayout(self)

        # Image
        img_lbl = QtWidgets.QLabel()
        img_lbl.setAlignment(QtCore.Qt.AlignCenter)
        img_lbl.setFixedHeight(200)

        img_name = product.get("image_path", "")
        img_full = os.path.join(ASSETS_DIR, img_name)

        if img_name and os.path.exists(img_full):
            pix = QtGui.QPixmap(img_full).scaled(300, 200, QtCore.Qt.KeepAspectRatio)
            img_lbl.setPixmap(pix)
        else:
            img_lbl.setText("No image")

        layout.addWidget(img_lbl)

        # Text details
        layout.addWidget(QtWidgets.QLabel(f"<b>Name:</b> {product.get('name','')}"))
        layout.addWidget(QtWidgets.QLabel(f"<b>Category:</b> {product.get('category','')}"))
        layout.addWidget(QtWidgets.QLabel(f"<b>Material:</b> {product.get('material','')}"))
        layout.addWidget(QtWidgets.QLabel(f"<b>Price:</b> ₹{product.get('price',0)}"))

        desc = QtWidgets.QTextEdit()
        desc.setReadOnly(True)
        desc.setText(product.get("description", "No description"))
        layout.addWidget(QtWidgets.QLabel("<b>Description:</b>"))
        layout.addWidget(desc)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        try_on_btn = QtWidgets.QPushButton("Try On")
        try_on_btn.setStyleSheet("background-color: #FF6B9D; color: white; font-weight: bold;")
        try_on_btn.clicked.connect(lambda: self.try_on_product(product))
        btn_layout.addWidget(try_on_btn)

        # Quantity selector and Add to Cart in product details
        qty_lbl = QtWidgets.QLabel("Qty:")
        qty_lbl.setStyleSheet("font-size:11px; margin-left:8px;")
        qty_spin = QtWidgets.QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(99)
        qty_spin.setValue(1)
        qty_spin.setFixedWidth(70)
        btn_layout.addWidget(qty_lbl)
        btn_layout.addWidget(qty_spin)

        add_cart_btn = QtWidgets.QPushButton("Add to Cart")
        add_cart_btn.setStyleSheet("background-color: #B8D4E8; color: #333333; font-weight: bold;")
        add_cart_btn.clicked.connect(lambda: self.add_and_close(product, qty_spin.value()))
        btn_layout.addWidget(add_cart_btn)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def try_on_product(self, product):
        """Launch virtual try-on for this product."""
        try:
            from tryon.run import run_tryon
            run_tryon(product)
        except ImportError:
            QtWidgets.QMessageBox.warning(self, "Error", "Try-on feature not available. Missing tryon module.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Try-on failed: {str(e)}")

    def add_and_close(self, product, qty):
        """Add the product with selected qty to cart, then close dialog."""
        parent = self.parent()
        try:
            if parent and hasattr(parent, 'add_to_cart'):
                parent.add_to_cart(product, qty)
            else:
                # fallback: try direct cart attribute
                cart = getattr(parent, 'cart', None)
                if cart:
                    cart.add_item(product, qty)
                    QtWidgets.QMessageBox.information(self, "Added to Cart", f"Added {qty} x {product.get('name')}")
                else:
                    QtWidgets.QMessageBox.warning(self, "Cart Missing", "No cart available to add items.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Add to Cart Failed", f"Could not add item to cart: {e}")
        finally:
            self.accept()


# -----------------------
# MAIN USER PANEL WINDOW
# -----------------------
class UserPanel(QtWidgets.QMainWindow):
    def __init__(self, user_id="guest"):
        super().__init__()
        self.setWindowTitle("JewelMart — Luxury Jewelry Store")
        self.resize(1200, 800)
        self.user_id = user_id
        
        # Initialize shopping cart with user ID
        self.cart = ShoppingCart(user_id=user_id)
        
        # Light theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FAFAFA;
            }
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
            QLabel {
                color: #333333;
            }
        """)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with logo and search
        header = QtWidgets.QWidget()
        header.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        header_layout = QtWidgets.QVBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Logo
        logo = QtWidgets.QLabel("✨ JewelMart")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #C8937E;")
        header_layout.addWidget(logo)

        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search jewelry by name or category...")
        self.search.setMaximumWidth(500)
        self.search.returnPressed.connect(self.search_products)
        search_btn = QtWidgets.QPushButton("Search")
        search_btn.clicked.connect(self.search_products)
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_products)
        cart_btn = QtWidgets.QPushButton("🛒 View Cart")
        cart_btn.setStyleSheet("""
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
        cart_btn.clicked.connect(self.open_cart)
        
        search_layout.addWidget(self.search)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(refresh_btn)
        search_layout.addWidget(cart_btn)
        search_layout.addStretch()
        header_layout.addLayout(search_layout)

        main_layout.addWidget(header)

        # Main content area with category tabs
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Category tabs
        self.category_tabs = QtWidgets.QTabWidget()
        self.category_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #666666;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #E0E0E0;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #C8937E;
                border: 1px solid #E0E0E0;
                border-bottom: 2px solid #C8937E;
            }
        """)
        
        content_layout.addWidget(self.category_tabs)
        
        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color: #999999; font-size: 12px;")
        content_layout.addWidget(self.status)

        main_layout.addWidget(content)

        self.products = []
        self.category_dict = {}
        self.load_products()


    # -------- GRID CLEAR ----------
    def clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    # -------- LOAD PRODUCTS ----------
    def load_products(self):
        # Always fetch fresh data from database
        try:
            self.products = list(product_col.find())
        except Exception as e:
            print(f"Error loading products: {e}")
            self.products = []
        
        self.category_dict = {}
        
        # Group products by category
        for p in self.products:
            cat = p.get("category", "Other").strip()
            if cat not in self.category_dict:
                self.category_dict[cat] = []
            self.category_dict[cat].append(p)
        
        # Clear existing tabs
        self.category_tabs.clear()
        
        # Create tabs for each category
        for category in sorted(self.category_dict.keys()):
            products = self.category_dict[category]
            tab_widget = self.create_category_tab(category, products)
            self.category_tabs.addTab(tab_widget, category)
        
        self.status.setText(f"Loaded {len(self.products)} products across {len(self.category_dict)} categories")

    def create_category_tab(self, category, products):
        """Create a tab widget for a category with header image and product grid"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Category header (use first product's image as banner)
        if products:
            header_label = QtWidgets.QLabel(category.upper())
            header_label.setStyleSheet(f"""
                background-color: #F5D7C6;
                color: #333333;
                padding: 30px;
                font-size: 18px;
                font-weight: bold;
                border-bottom: 2px solid #E0B5A0;
            """)
            header_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(header_label)
        
        # Scroll area for products
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #FAFAFA; }")
        
        # Product grid container
        grid_container = QtWidgets.QWidget()
        grid_container.setStyleSheet("background-color: #FAFAFA;")
        grid = QtWidgets.QGridLayout(grid_container)
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)
        
        # Add products to grid (4 columns)
        col = 0
        row = 0
        for product in products:
            product_card = self.create_product_card(product)
            grid.addWidget(product_card, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        grid.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding), row + 1, 0, 1, 4)
        
        scroll.setWidget(grid_container)
        layout.addWidget(scroll)
        
        return container

    # -------- SEARCH ----------
    def search_products(self):
        text = self.search.text().strip().lower()
        if not text:
            self.load_products()
            return

        results = []
        for p in self.products:
            if (text in p.get("name","").lower()) or (text in p.get("category","").lower()):
                results.append(p)

        # Create a single tab with search results
        self.category_tabs.clear()
        if results:
            search_tab = self.create_category_tab("Search Results", results)
            self.category_tabs.addTab(search_tab, f"Search Results ({len(results)})")
        
        self.status.setText(f"Found {len(results)} products")

    # -------- RENDER PRODUCTS ----------
    def render_products(self, products):
        """Legacy method - not used in new design"""
        pass

    # -------- CREATE PRODUCT CARD ----------
    def create_product_card(self, product):
        """Create a modern product card with light theme"""
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E8E8E8;
                border-radius: 4px;
            }
            QFrame:hover {
                border: 1px solid #D0B5A0;
            }
        """)
        card.setFixedSize(260, 350)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image container
        img_container = QtWidgets.QWidget()
        img_container.setStyleSheet("background-color: #F5F5F5;")
        img_layout = QtWidgets.QVBoxLayout(img_container)
        img_layout.setContentsMargins(0, 0, 0, 0)
        
        img = QtWidgets.QLabel()
        img.setFixedHeight(140)
        img.setAlignment(QtCore.Qt.AlignCenter)

        img_name = product.get("image_path", "")
        img_full = os.path.join(ASSETS_DIR, img_name)

        if img_name and os.path.exists(img_full):
            pix = QtGui.QPixmap(img_full).scaled(240, 130, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            img.setPixmap(pix)
        else:
            img.setText("No image")
            img.setStyleSheet("color: #CCCCCC;")

        img_layout.addWidget(img)
        layout.addWidget(img_container)

        # Content area
        content = QtWidgets.QWidget()
        content.setStyleSheet("background-color: #FFFFFF;")
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(5)

        # Product name
        name_label = QtWidgets.QLabel(product.get('name', ''))
        name_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 12px;")
        name_label.setWordWrap(True)
        content_layout.addWidget(name_label)

        # Category and material
        cat_mat = QtWidgets.QLabel(f"{product.get('category', '')} | {product.get('material', '')}")
        cat_mat.setStyleSheet("color: #999999; font-size: 10px;")
        content_layout.addWidget(cat_mat)

        # Price
        price_label = QtWidgets.QLabel(f"₹{product.get('price', 0)}")
        price_label.setStyleSheet("font-weight: bold; color: #C8937E; font-size: 13px;")
        content_layout.addWidget(price_label)

        content_layout.addStretch()
        layout.addWidget(content)

        # Button area
        button_area = QtWidgets.QWidget()
        button_area.setStyleSheet("background-color: #FFFFFF;")
        button_layout = QtWidgets.QVBoxLayout(button_area)
        button_layout.setContentsMargins(8, 5, 8, 8)
        button_layout.setSpacing(5)

        # View Details button
        view_btn = QtWidgets.QPushButton("View Details")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5D7C6;
                color: #333333;
                border: none;
                border-radius: 3px;
                padding: 7px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #E8BFB0;
            }
        """)
        view_btn.clicked.connect(lambda: self.open_details(product))
        button_layout.addWidget(view_btn)

        # Try On button
        tryon_btn = QtWidgets.QPushButton("Try On")
        tryon_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8C5C9;
                color: #333333;
                border: none;
                border-radius: 3px;
                padding: 7px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #DDB5BE;
            }
        """)
        tryon_btn.clicked.connect(lambda: self.launch_tryon(product))
        button_layout.addWidget(tryon_btn)

        # Quantity selector + Add to Cart button
        qty_widget = QtWidgets.QWidget()
        qty_layout = QtWidgets.QHBoxLayout(qty_widget)
        qty_layout.setContentsMargins(0, 0, 0, 0)
        qty_layout.setSpacing(6)
        qty_label = QtWidgets.QLabel("Qty:")
        qty_label.setStyleSheet("font-size:11px;")
        qty_spin = QtWidgets.QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(99)
        qty_spin.setValue(1)
        qty_spin.setFixedWidth(60)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(qty_spin)
        qty_layout.addStretch()
        button_layout.addWidget(qty_widget)

        cart_btn = QtWidgets.QPushButton("Add to Cart")
        cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8D4E8;
                color: #333333;
                border: none;
                border-radius: 3px;
                padding: 7px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #A0C8E0;
            }
        """)
        cart_btn.clicked.connect(lambda _, p=product, q=qty_spin: self.add_to_cart(p, q.value()))
        button_layout.addWidget(cart_btn)

        layout.addWidget(button_area)

        return card

    # -------- MAKE CARD (Legacy) ----------
    def make_card(self, p):
        """Legacy method - not used in new design"""
        return self.create_product_card(p)


    # -------- OPEN DETAILS ----------
    def open_details(self, product):
        dlg = ProductDetails(product, self)
        dlg.exec_()

    # -------- LAUNCH TRY-ON ----------
    def launch_tryon(self, product):
        """Launch virtual try-on for this product."""
        try:
            from tryon.run import run_tryon
            run_tryon(product)
        except (ImportError, ModuleNotFoundError):
            QtWidgets.QMessageBox.information(self, "Try-On Coming Soon", 
                f"Virtual try-on for '{product.get('name')}' is coming soon!\n\n"
                "This feature is under development. Please check back later.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Try-on failed: {str(e)}")

    # -------- ADD TO CART ----------
    def add_to_cart(self, product, qty=1):
        """Add a product to the shopping cart with specified quantity."""
        try:
            new_qty = self.cart.add_item(product, qty)
            QtWidgets.QMessageBox.information(self, "Added to Cart", 
                f"'{product.get('name')}' has been added to your cart! (Added Qty: {qty}, Total Qty: {new_qty})")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Cart Error", f"Failed to add to cart: {e}")

    # -------- VIEW CART ----------
    def open_cart(self):
        """Open the shopping cart dialog."""
        dlg = CartDialog(self.cart, self)
        dlg.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserPanel()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()