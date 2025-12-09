# user_panel.py
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import sys, os
import cv2
import numpy as np
import threading
from pymongo import MongoClient

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
VIDEO_PATH = os.path.join(ASSETS_DIR, "JewelMart.mp4")
# Alternative video formats to try
ALT_VIDEO_PATHS = [
    os.path.join(ASSETS_DIR, "JewelMart.avi"),
    os.path.join(ASSETS_DIR, "JewelMart.mkv"),
    os.path.join(ASSETS_DIR, "JewelMart.mov"),
]


# -----------------------
# HOME PAGE WITH VIDEO
# -----------------------
# -----------------------
# HOME PAGE WITH VIDEO (Using OpenCV)
# -----------------------
class VideoPlayer(QtWidgets.QWidget):
    """OpenCV-based video player for better compatibility"""
    frame_updated = QtCore.pyqtSignal(np.ndarray)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.cap = None
        self.is_playing = False
        self.is_looping = True
        self.thread = None
        self.current_frame = None
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video label to display frames
        self.video_label = QtWidgets.QLabel()
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setScaledContents(True)  # Scale to fit
        self.video_label.setMinimumSize(400, 300)
        layout.addWidget(self.video_label)
        
        # Connect signal
        self.frame_updated.connect(self.on_frame_updated)
        
        # Start playing
        self.play()
    
    def play(self):
        """Start video playback"""
        if self.is_playing:
            return
        
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                print(f"Failed to open video: {self.video_path}")
                return
            
            self.is_playing = True
            self.thread = threading.Thread(target=self.play_video_thread, daemon=True)
            self.thread.start()
            print("Video playback started (OpenCV)")
            
        except Exception as e:
            print(f"Error opening video: {e}")
    
    def play_video_thread(self):
        """Background thread for video playback"""
        while self.is_playing:
            ret, frame = self.cap.read()
            
            if not ret:
                # Video ended, restart if looping
                if self.is_looping:
                    print("Video ended, restarting loop")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            # Scale frame to maintain aspect ratio while filling parent
            h, w = frame.shape[:2]
            self.current_frame = frame
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Emit frame signal
            self.frame_updated.emit(frame_rgb)
            
            # Control playback speed (30 FPS)
            QtCore.QThread.msleep(33)
    
    def on_frame_updated(self, frame):
        """Display frame on label"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        
        # Scale to fit label while maintaining aspect ratio
        label_size = self.video_label.size()
        if label_size.width() > 0 and label_size.height() > 0:
            pixmap = QtGui.QPixmap.fromImage(qt_image).scaledToHeight(
                label_size.height(), 
                QtCore.Qt.SmoothTransformation
            )
        else:
            pixmap = QtGui.QPixmap.fromImage(qt_image)
        
        self.video_label.setPixmap(pixmap)
    
    def resizeEvent(self, event):
        """Handle resize events to maintain aspect ratio"""
        super().resizeEvent(event)
        # Redraw current frame at new size if available
        if self.current_frame is not None:
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            self.on_frame_updated(frame_rgb)
    
    def stop(self):
        """Stop video playback"""
        self.is_playing = False
        if self.cap:
            self.cap.release()
        if self.thread:
            self.thread.join(timeout=1)
        print("Video playback stopped")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.stop()
        super().closeEvent(event)


class HomePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setStyleSheet("background: #000000;")  # Black background for full-screen effect

        self.video_player = None
        self.video_loaded = False
        
        # Try to load video - first try main path, then alternatives
        video_to_load = None
        if os.path.exists(VIDEO_PATH):
            video_to_load = VIDEO_PATH
        else:
            # Try alternative formats
            for alt_path in ALT_VIDEO_PATHS:
                if os.path.exists(alt_path):
                    video_to_load = alt_path
                    print(f"Main video not found, using: {alt_path}")
                    break
        
        if video_to_load:
            try:
                # Create OpenCV-based video player
                self.video_player = VideoPlayer(video_to_load)
                layout.addWidget(self.video_player, 1)  # Stretch to fill
                self.video_loaded = True
                print(f"Video loaded from: {video_to_load}")
                
            except Exception as e:
                print(f"Error loading video: {e}")
                self.show_fallback(layout)
                self.video_loaded = False
        else:
            print(f"Video file not found")
            self.show_fallback(layout)
            self.video_loaded = False
    
    def show_fallback(self, layout):
        """Show elegant fallback home page"""
        # Main container
        main_container = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a banner-like header
        header_widget = QtWidgets.QWidget()
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #C8937E, stop:1 #D4A895);
        """)
        header_widget.setFixedHeight(300)
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)
        header_layout.addStretch()
        
        # Logo/Title
        logo = QtWidgets.QLabel("✨ JewelMart ✨")
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setStyleSheet("font-size: 56px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(logo)
        
        # Tagline
        tagline = QtWidgets.QLabel("Luxury Jewelry Store")
        tagline.setAlignment(QtCore.Qt.AlignCenter)
        tagline.setStyleSheet("font-size: 20px; color: #FFFFFF; font-style: italic;")
        header_layout.addWidget(tagline)
        
        header_layout.addStretch()
        main_layout.addWidget(header_widget)
        
        # Content area
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setSpacing(30)
        
        # Welcome message
        welcome = QtWidgets.QLabel("Welcome to JewelMart")
        welcome.setAlignment(QtCore.Qt.AlignCenter)
        welcome.setStyleSheet("font-size: 28px; font-weight: bold; color: #C8937E;")
        content_layout.addWidget(welcome)
        
        # Description
        description = QtWidgets.QLabel(
            "Discover our exquisite collection of luxury jewelry\n"
            "Handcrafted with precision, elegance, and timeless beauty\n\n"
            "From stunning earrings to elegant necklaces,\n"
            "every piece tells a unique story of craftsmanship"
        )
        description.setAlignment(QtCore.Qt.AlignCenter)
        description.setStyleSheet("font-size: 14px; color: #666666; line-height: 1.6;")
        description.setWordWrap(True)
        content_layout.addWidget(description)
        
        content_layout.addStretch()
        
        main_layout.addWidget(content_widget)
        layout.addWidget(main_container)
    
    def stop_video(self):
        """Stop video when leaving home page"""
        if self.video_player and self.video_loaded:
            self.video_player.stop()
            print("Video playback stopped")


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


# -----------------------
# MAIN USER PANEL WINDOW
# -----------------------
class UserPanel(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart — Luxury Jewelry Store")
        self.resize(1200, 800)
        
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

        # Top row: Logo and title
        top_row = QtWidgets.QHBoxLayout()
        
        # Logo image
        logo_img = QtWidgets.QLabel()
        logo_path = os.path.join(ASSETS_DIR, "JewelMart.png")
        if os.path.exists(logo_path):
            pixmap = QtGui.QPixmap(logo_path).scaledToHeight(40, QtCore.Qt.SmoothTransformation)
            logo_img.setPixmap(pixmap)
        else:
            logo_img.setText("Logo")
        logo_img.setFixedWidth(50)
        top_row.addWidget(logo_img)
        
        # Logo
        logo = QtWidgets.QLabel("JewelMart")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #C8937E;")
        top_row.addWidget(logo)
        top_row.addStretch()
        header_layout.addLayout(top_row)

        # Search bar with category button
        search_layout = QtWidgets.QHBoxLayout()
        
        # Home button
        home_btn = QtWidgets.QPushButton("🏠 Home")
        home_btn.clicked.connect(self.show_home)
        search_layout.addWidget(home_btn)
        
        # Search field
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search jewelry by name or category...")
        self.search.setMaximumWidth(400)
        self.search.returnPressed.connect(self.search_products)
        search_btn = QtWidgets.QPushButton("Search")
        search_btn.clicked.connect(self.search_products)
        
        # Category dropdown button
        self.category_btn = QtWidgets.QPushButton("📂 Categories")
        self.category_btn.clicked.connect(self.show_category_menu)
        
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_products)
        
        search_layout.addWidget(self.search)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(self.category_btn)
        search_layout.addWidget(refresh_btn)
        search_layout.addStretch()
        header_layout.addLayout(search_layout)

        main_layout.addWidget(header)

        # Stacked widget for home page and products page
        self.stacked = QtWidgets.QStackedWidget()
        
        # Home page
        self.home_page = HomePage()
        self.stacked.addWidget(self.home_page)
        
        # Products page
        products_widget = QtWidgets.QWidget()
        products_layout = QtWidgets.QVBoxLayout(products_widget)
        products_layout.setContentsMargins(20, 20, 20, 20)
        products_layout.setSpacing(15)

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
        
        products_layout.addWidget(self.category_tabs)
        
        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color: #999999; font-size: 12px;")
        products_layout.addWidget(self.status)

        self.stacked.addWidget(products_widget)
        main_layout.addWidget(self.stacked)

        self.products = []
        self.category_dict = {}
        self.load_products()
        self.show_home()

    # -------- SHOW HOME PAGE ----------
    def show_home(self):
        """Show home page with video"""
        self.stacked.setCurrentIndex(0)
        # Video should start automatically in OpenCV player

    def show_category_menu(self):
        """Show category menu"""
        self.stacked.setCurrentIndex(1)
        self.home_page.stop_video()

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
            self.show_category_menu()
            self.load_products()
            return

        # Switch to products page
        self.stacked.setCurrentIndex(1)
        self.home_page.stop_video()

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
        except ImportError:
            QtWidgets.QMessageBox.warning(self, "Error", "Try-on feature not available. Missing tryon module.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Try-on failed: {str(e)}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserPanel()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()