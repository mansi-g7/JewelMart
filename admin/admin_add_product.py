# admin_add_product.py
# Put this file inside JewelMart/admin/
from PyQt5 import QtWidgets, QtGui, QtCore
import sys, os, json, shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # .../JewelMart/admin
PROJECT_ROOT = os.path.dirname(BASE_DIR)                   # .../JewelMart
CATALOG_PATH = os.path.join(PROJECT_ROOT, "catalog.json")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

CATEGORIES = ["Necklace", "Earring", "Ring", "Bracelet", "Nose Pin", "Bangle"]

def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        return []
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_catalog(items):
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

class AddProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Product — Admin")
        self.resize(520, 420)

        layout = QtWidgets.QFormLayout(self)

        self.name = QtWidgets.QLineEdit()
        self.category = QtWidgets.QComboBox(); self.category.addItems(CATEGORIES)
        self.material = QtWidgets.QLineEdit()
        self.price = QtWidgets.QLineEdit()
        self.description = QtWidgets.QTextEdit()
        self.image_path = QtWidgets.QLineEdit()
        self.image_btn = QtWidgets.QPushButton("Choose Image")
        self.image_btn.clicked.connect(self.choose_image)

        layout.addRow("Product name:", self.name)
        layout.addRow("Category:", self.category)
        layout.addRow("Material:", self.material)
        layout.addRow("Price (numeric):", self.price)

        h = QtWidgets.QHBoxLayout()
        h.addWidget(self.image_path)
        h.addWidget(self.image_btn)
        layout.addRow("Image:", h)

        layout.addRow("Description:", self.description)

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
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select product image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.image_path.setText(path)

class AdminAddWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart — Admin Add Product")
        self.resize(900, 600)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)

        top_h = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit(); self.search.setPlaceholderText("Search by name or category...")
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_products)
        add_btn = QtWidgets.QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        top_h.addWidget(self.search)
        top_h.addWidget(refresh_btn)
        top_h.addWidget(add_btn)

        v.addLayout(top_h)

        # Scroll area with grid of product cards (modern UI)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(12,12,12,12)
        self.scroll.setWidget(self.grid_container)
        v.addWidget(self.scroll)

        # status / details
        self.status = QtWidgets.QLabel("")
        v.addWidget(self.status)

        self.products = []
        self.load_products()

    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_products(self):
        self.products = load_catalog()
        self.render_products(self.products)
        self.status.setText(f"Loaded {len(self.products)} products")

    def render_products(self, products):
        self.clear_grid()
        cols = 3
        row = col = 0
        for p in products:
            card = self.make_card(p)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= cols:
                col = 0; row += 1

    def make_card(self, p):
        widget = QtWidgets.QFrame()
        widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        widget.setFixedSize(260, 180)
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(8,8,8,8)

        # Image area
        img_lbl = QtWidgets.QLabel()
        img_lbl.setFixedHeight(90)
        img_lbl.setAlignment(QtCore.Qt.AlignCenter)
        img_path = p.get("image_path", "")
        img_full = ""
        if img_path:
            img_full = img_path if os.path.isabs(img_path) else os.path.join(PROJECT_ROOT, "assets", os.path.basename(img_path))
        if img_full and os.path.exists(img_full):
            pix = QtGui.QPixmap(img_full).scaled(200, 90, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            img_lbl.setPixmap(pix)
        else:
            # placeholder
            img_lbl.setText("No image")
        layout.addWidget(img_lbl)

        # title / price
        title = QtWidgets.QLabel(f"{p.get('name','(no name)')}")
        title.setStyleSheet("font-weight:600;")
        layout.addWidget(title)
        sub = QtWidgets.QLabel(f"{p.get('category','')} — {p.get('material','')}")
        sub.setStyleSheet("color:gray; font-size:11px;")
        layout.addWidget(sub)

        bottom = QtWidgets.QHBoxLayout()
        price_lbl = QtWidgets.QLabel(f"₹{p.get('price',0)}")
        bottom.addWidget(price_lbl)
        bottom.addStretch()
        del_btn = QtWidgets.QPushButton("Delete")
        del_btn.setProperty("pid", p.get("id"))
        del_btn.clicked.connect(self.delete_product)
        bottom.addWidget(del_btn)
        layout.addLayout(bottom)

        return widget

    def add_product(self):
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

        # calculate new ID
        max_id = 0
        for p in self.products:
            try:
                if int(p.get("id", 0)) > max_id:
                    max_id = int(p.get("id", 0))
            except Exception:
                pass
        new_id = max_id + 1

        img_target_name = ""
        if img_src and os.path.exists(img_src):
            os.makedirs(ASSETS_DIR, exist_ok=True)
            img_target_name = f"product_{new_id}_" + os.path.basename(img_src)
            img_target = os.path.join(ASSETS_DIR, img_target_name)
            try:
                shutil.copyfile(img_src, img_target)
                img_target_name = img_target_name
            except Exception:
                img_target_name = ""

        new_prod = {
            "id": new_id,
            "name": name,
            "category": category,
            "material": material,
            "price": price,
            "image_path": img_target_name,
            "description": desc
        }

        # append and save
        self.products.append(new_prod)
        try:
            save_catalog(self.products)
            QtWidgets.QMessageBox.information(self, "Saved", "Product added.")
            self.load_products()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save product: {e}")

    def delete_product(self):
        btn = self.sender()
        pid = btn.property("pid")
        if pid is None:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Delete", "Delete this product?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        # remove product with id
        self.products = [p for p in self.products if p.get("id") != pid]
        save_catalog(self.products)
        self.load_products()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = AdminAddWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
