# admin_add_product.py
from PyQt5 import QtWidgets, QtGui, QtCore
import sys, os, shutil
from pymongo import MongoClient

# -----------------------
#  MONGODB CONNECTION
# -----------------------
from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["JewelMart"]
    print("CONNECTED:", db.list_collection_names())
except Exception as e:
    print("ERROR:", e)










client = MongoClient("mongodb://localhost:27017/")
db = client["JewelMart"]
product_col = db["jewel_add"]     # <-- your real collection name

BASE_DIR = os.path.dirname(os.path.abspath(__file__))     
PROJECT_ROOT = os.path.dirname(BASE_DIR)                  
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

CATEGORIES = ["Necklace", "Earring", "Ring", "Bracelet", "Nose Pin", "Bangle"]


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
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select product image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
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
        self.search = QtWidgets.QLineEdit(); 
        self.search.setPlaceholderText("Search by name or category...")
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_products)
        add_btn = QtWidgets.QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        top_h.addWidget(self.search)
        top_h.addWidget(refresh_btn)
        top_h.addWidget(add_btn)
        v.addLayout(top_h)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_container = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.scroll.setWidget(self.grid_container)
        v.addWidget(self.scroll)

        self.status = QtWidgets.QLabel("")
        v.addWidget(self.status)

        self.products = []
        self.load_products()

    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def load_products(self):
        self.products = list(product_col.find())
        self.render_products(self.products)
        self.status.setText(f"Loaded {len(self.products)} products")

    def render_products(self, products):
        self.clear_grid()
        row = col = 0
        for p in products:
            card = self.make_card(p)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                row += 1
                col = 0

    def make_card(self, p):
        widget = QtWidgets.QFrame()
        widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        widget.setFixedSize(260, 180)

        layout = QtWidgets.QVBoxLayout(widget)

        img_lbl = QtWidgets.QLabel()
        img_lbl.setFixedHeight(90)
        img_lbl.setAlignment(QtCore.Qt.AlignCenter)

        img_name = p.get("image_path", "")
        img_full = os.path.join(ASSETS_DIR, img_name) if img_name else ""

        if img_name and os.path.exists(img_full):
            pix = QtGui.QPixmap(img_full).scaled(200, 90, QtCore.Qt.KeepAspectRatio)
            img_lbl.setPixmap(pix)
        else:
            img_lbl.setText("No image")

        layout.addWidget(img_lbl)

        layout.addWidget(QtWidgets.QLabel(p.get("name", "")))
        layout.addWidget(QtWidgets.QLabel(f"{p.get('category','')} — {p.get('material','')}"))

        bottom = QtWidgets.QHBoxLayout()
        bottom.addWidget(QtWidgets.QLabel(f"₹{p.get('price',0)}"))
        bottom.addStretch()

        del_btn = QtWidgets.QPushButton("Delete")
        del_btn.clicked.connect(lambda: self.delete_product(p["_id"]))
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
            price = int(dlg.price.text())
        except:
            price = 0

        desc = dlg.description.toPlainText().strip()
        img_src = dlg.image_path.text().strip()

        # copy image
        img_filename = ""
        if img_src and os.path.exists(img_src):
            os.makedirs(ASSETS_DIR, exist_ok=True)
            img_filename = os.path.basename(img_src)
            shutil.copy(img_src, os.path.join(ASSETS_DIR, img_filename))

        new_product = {
            "name": name,
            "category": category,
            "material": material,
            "price": price,
            "description": desc,
            "image_path": img_filename
        }

        product_col.insert_one(new_product)

        QtWidgets.QMessageBox.information(self, "Saved", "Product added to MongoDB.")
        self.load_products()

    def delete_product(self, pid):
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Delete",
            "Delete this product?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            product_col.delete_one({"_id": pid})
            self.load_products()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = AdminAddWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
