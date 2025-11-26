from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
USERS_FILE = os.path.join(PROJECT_ROOT, "users.json")
CATALOG_PATH = os.path.join(PROJECT_ROOT, "catalog.json")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

try:
    from data import categories, get_products
except Exception:
    categories = ["Necklace", "Earring", "Nose Pin"]
    def get_products(category=None):
        return []


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_catalog():
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # fallback: try to read from data.get_products()
        try:
            return get_products()
        except Exception:
            return []


def save_catalog(products):
    try:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2)
        return True
    except Exception:
        return False


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


class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart - Admin Panel")
        self.resize(800, 600)

        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        # Users tab
        users_w = QtWidgets.QWidget()
        users_layout = QtWidgets.QVBoxLayout(users_w)
        self.users_list = QtWidgets.QListWidget()
        users_layout.addWidget(self.users_list)
        refresh_users = QtWidgets.QPushButton("Refresh")
        refresh_users.clicked.connect(self.load_users_into_list)
        users_layout.addWidget(refresh_users)
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

        self.load_users_into_list()
        self.load_catalog_into_list()

    def load_users_into_list(self):
        self.users_list.clear()
        users = load_users()
        for email, info in users.items():
            name = info.get("name", "")
            self.users_list.addItem(f"{email} — {name}")

    def load_catalog_into_list(self):
        self.cat_list.clear()
        self.products = load_catalog()
        for p in self.products:
            item = QtWidgets.QListWidgetItem(p.get("name", "(no name)"))
            # try to set an icon
            img = p.get("image_path")
            if img:
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
        lines = [f"ID: {p.get('id')}", f"Name: {p.get('name')}", f"Category: {p.get('category')}", f"Material: {p.get('material')}", f"Price: {p.get('price')}", f"Image: {p.get('image_path')}", "", p.get('description','')]
        self.detail.setPlainText("\n".join(str(x) for x in lines))

    def add_product(self):
        dlg = AddProductDialog(self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        # Build product dict
        name = dlg.name.text().strip()
        category = dlg.category.currentText()
        material = dlg.material.text().strip()
        try:
            price = int(dlg.price.text().strip())
        except Exception:
            price = 0
        desc = dlg.description.toPlainText().strip()
        img_src = dlg.image_path.text().strip()

        # determine new id
        max_id = 0
        for p in self.products:
            try:
                if int(p.get("id", 0)) > max_id:
                    max_id = int(p.get("id", 0))
            except Exception:
                pass
        new_id = max_id + 1

        img_target_name = None
        if img_src and os.path.exists(img_src):
            os.makedirs(ASSETS_DIR, exist_ok=True)
            img_target_name = f"product_{new_id}_" + os.path.basename(img_src)
            img_target = os.path.join(ASSETS_DIR, img_target_name)
            try:
                shutil.copyfile(img_src, img_target)
                # store relative basename so data loader can resolve
                img_target_name = img_target_name
            except Exception:
                img_target_name = None

        new_prod = {
            "id": new_id,
            "name": name,
            "category": category,
            "material": material,
            "price": price,
            "image_path": img_target_name or "",
            "description": desc,
        }
        self.products.append(new_prod)
        if save_catalog(self.products):
            QtWidgets.QMessageBox.information(self, "Saved", "Product saved to catalog.json")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to save catalog.json")
        self.load_catalog_into_list()

    def delete_selected(self):
        sel = self.cat_list.currentRow()
        if sel < 0 or sel >= len(self.products):
            return
        confirm = QtWidgets.QMessageBox.question(self, "Delete", "Delete selected product?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        prod = self.products.pop(sel)
        if save_catalog(self.products):
            QtWidgets.QMessageBox.information(self, "Deleted", "Product removed from catalog.json")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to update catalog.json")
        self.load_catalog_into_list()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = AdminWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
