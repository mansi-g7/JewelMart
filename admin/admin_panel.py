from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import json
import shutil

# import the helper that returns the admin namespace/database object
# this is the function from your fixed database.py
from database import get_admin_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
USERS_FILE = os.path.join(PROJECT_ROOT, "users.json")   # kept as fallback / migration source
CATALOG_PATH = os.path.join(PROJECT_ROOT, "catalog.json")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# categories/data fallback if you don't have a data.py
try:
    from data import categories, get_products
except Exception:
    categories = ["Necklace", "Earring", "Nose Pin"]
    def get_products(category=None):
        return []

# -----------------------
# Migration helper (optional)
# -----------------------
def migrate_json_catalog_to_mongo():
    """
    One-time helper: if you have an existing catalog.json, import it to MongoDB.
    Call this manually if you want to migrate.
    """
    db = get_admin_db()
    products_coll = db["products"]
    if not os.path.exists(CATALOG_PATH):
        return False, "No local catalog.json found"
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        return False, f"Failed reading catalog.json: {e}"

    # insert/update each product by its 'id' field (upsert)
    for p in products:
        pid = p.get("id")
        if pid is None:
            continue
        products_coll.update_one({"id": pid}, {"$set": p}, upsert=True)
    return True, f"Migrated {len(products)} products to MongoDB"


# -----------------------
# Admin UI Dialogs
# -----------------------
class AddProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Product")
        self.resize(400, 300)
        layout = QtWidgets.QFormLayout(self)
        self.name = QtWidgets.QLineEdit()
        self.category = QtWidgets.QComboBox()
        self.category.addItems(categories)
        self.material = QtWidgets.QLineEdit()
        self.price = QtWidgets.QLineEdit()
        self.description = QtWidgets.QTextEdit()
        self.image_path = QtWidgets.QLineEdit()
        self.image_btn = QtWidgets.QPushButton("Choose Image")
        self.image_btn.clicked.connect(self.choose_image)

        layout.addRow("Name:", self.name)
        layout.addRow("Category:", self.category)
        layout.addRow("Material:", self.material)
        layout.addRow("Price (numeric):", self.price)
        layout.addRow("Image:", self.image_path)
        layout.addRow("", self.image_btn)
        layout.addRow("Description:", self.description)

        btns = QtWidgets.QHBoxLayout()
        save = QtWidgets.QPushButton("Save")
        cancel = QtWidgets.QPushButton("Cancel")
        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addRow(btns)

    def choose_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path.setText(path)


# -----------------------
# Admin main window
# -----------------------
class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart - Admin Panel")
        self.resize(900, 650)

        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        # Users tab (reads from users collection; also shows fallback to local users.json)
        users_w = QtWidgets.QWidget()
        users_layout = QtWidgets.QVBoxLayout(users_w)
        self.users_list = QtWidgets.QListWidget()
        users_layout.addWidget(self.users_list)
        refresh_users = QtWidgets.QPushButton("Refresh")
        refresh_users.clicked.connect(self.load_users_into_list)
        users_layout.addWidget(refresh_users)
        migrate_btn = QtWidgets.QPushButton("Migrate local catalog.json → MongoDB")
        migrate_btn.clicked.connect(self.run_migration)
        users_layout.addWidget(migrate_btn)
        tabs.addTab(users_w, "Users")

        # Catalog tab
        cat_w = QtWidgets.QWidget()
        cat_layout = QtWidgets.QVBoxLayout(cat_w)
        self.cat_list = QtWidgets.QListWidget()
        self.cat_list.itemClicked.connect(self.show_product_details)
        cat_layout.addWidget(self.cat_list)

        h = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        del_btn = QtWidgets.QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_selected)
        h.addWidget(add_btn)
        h.addWidget(del_btn)
        cat_layout.addLayout(h)

        self.detail = QtWidgets.QTextEdit()
        self.detail.setReadOnly(True)
        cat_layout.addWidget(self.detail)

        tabs.addTab(cat_w, "Catalog")

        # load initial data
        self.db = get_admin_db()
        self.products = []   # local cache for UI (list of dicts)
        self.load_users_into_list()
        self.load_catalog_into_list()

    # -----------------------
    # Users
    # -----------------------
    def load_users_into_list(self):
        """
        Load users from MongoDB users collection. If no users found and local users.json exists,
        show its contents as fallback.
        """
        self.users_list.clear()
        users_coll = self.db["users"]
        try:
            found = list(users_coll.find())
            if found:
                for u in found:
                    email = u.get("email", u.get("_id", "unknown"))
                    name = u.get("name", "")
                    self.users_list.addItem(f"{email} — {name}")
                return
        except Exception:
            # fallthrough to local file fallback
            pass

        # fallback to local users.json
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
            for email, info in users.items():
                name = info.get("name", "")
                self.users_list.addItem(f"{email} — {name}")
        except Exception:
            # nothing to show
            pass

    # -----------------------
    # Catalog / Products
    # -----------------------
    def load_catalog_into_list(self):
        """
        Load products from MongoDB 'products' collection and populate the UI list.
        """
        self.cat_list.clear()
        products_coll = self.db["products"]

        try:
            # get all products sorted by id ascending if id exists
            cursor = products_coll.find().sort("id", 1)
            self.products = list(cursor)
        except Exception:
            # fallback to local catalog.json reading
            try:
                with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                    self.products = json.load(f)
            except Exception:
                self.products = []

        for p in self.products:
            item = QtWidgets.QListWidgetItem(p.get("name", "(no name)"))
            img = p.get("image_path")
            if img:
                # if image path is absolute use it, otherwise look in assets by basename
                img_path = img if os.path.isabs(img) else os.path.join(ASSETS_DIR, os.path.basename(img))
                if os.path.exists(img_path):
                    pix = QtGui.QPixmap(img_path).scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    item.setIcon(QtGui.QIcon(pix))
            self.cat_list.addItem(item)

    def show_product_details(self, item):
        idx = self.cat_list.row(item)
        if idx < 0 or idx >= len(self.products):
            return
        p = self.products[idx]
        lines = [
            f"ID: {p.get('id')}",
            f"Name: {p.get('name')}",
            f"Category: {p.get('category')}",
            f"Material: {p.get('material')}",
            f"Price: {p.get('price')}",
            f"Image: {p.get('image_path')}",
            "",
            p.get('description', '')
        ]
        self.detail.setPlainText("\n".join(str(x) for x in lines))

    def add_product(self):
        """
        Collect fields from dialog, copy image into assets/, then insert new product into MongoDB.
        """
        dlg = AddProductDialog(self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return

        name = dlg.name.text().strip()
        category = dlg.category.currentText()
        material = dlg.material.text().strip()
        try:
            price = int(dlg.price.text().strip())
        except Exception:
            price = 0
        desc = dlg.description.toPlainText().strip()
        img_src = dlg.image_path.text().strip()

        products_coll = self.db["products"]

        # compute new numeric id: find max existing id
        max_doc = products_coll.find_one(sort=[("id", -1)])
        max_id = max_doc.get("id", 0) if max_doc else 0
        new_id = int(max_id) + 1

        img_target_name = ""
        if img_src and os.path.exists(img_src):
            os.makedirs(ASSETS_DIR, exist_ok=True)
            img_target_name = f"product_{new_id}_" + os.path.basename(img_src)
            img_target = os.path.join(ASSETS_DIR, img_target_name)
            try:
                shutil.copyfile(img_src, img_target)
                img_target_name = img_target_name  # stored as basename (relative)
            except Exception:
                img_target_name = ""

        new_prod = {
            "id": new_id,
            "name": name,
            "category": category,
            "material": material,
            "price": price,
            "image_path": img_target_name,
            "description": desc,
        }

        try:
            products_coll.insert_one(new_prod)
            QtWidgets.QMessageBox.information(self, "Saved", "Product saved to MongoDB (products collection).")
        except Exception as e:
            # As fallback, append to catalog.json
            try:
                # read existing
                local_products = []
                if os.path.exists(CATALOG_PATH):
                    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                        local_products = json.load(f)
                local_products.append(new_prod)
                with open(CATALOG_PATH, "w", encoding="utf-8") as f:
                    json.dump(local_products, f, indent=2)
                QtWidgets.QMessageBox.warning(self, "DB Error", f"Failed to insert to DB; saved to catalog.json instead.\n{e}")
            except Exception:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save product: {e}")

        self.load_catalog_into_list()

    def delete_selected(self):
        """
        Delete the selected product from MongoDB (by product 'id').
        """
        sel = self.cat_list.currentRow()
        if sel < 0 or sel >= len(self.products):
            return
        confirm = QtWidgets.QMessageBox.question(self, "Delete", "Delete selected product?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        prod = self.products.pop(sel)
        pid = prod.get("id")
        try:
            products_coll = self.db["products"]
            if pid is not None:
                products_coll.delete_one({"id": pid})
            QtWidgets.QMessageBox.information(self, "Deleted", "Product removed.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to delete from DB: {e}")

        # remove image file if exists (optional)
        img = prod.get("image_path")
        if img:
            img_path = img if os.path.isabs(img) else os.path.join(ASSETS_DIR, os.path.basename(img))
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass

        self.load_catalog_into_list()

    def run_migration(self):
        ok, msg = migrate_json_catalog_to_mongo()
        if ok:
            QtWidgets.QMessageBox.information(self, "Migration", msg)
        else:
            QtWidgets.QMessageBox.warning(self, "Migration", msg)

# -----------------------
# App entrypoint
# -----------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = AdminWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
