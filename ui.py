"""JewelMart UI - PyQt5 application with video home page and virtual try-on."""

import os
import json
import importlib.util
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets

try:
    from PyQt5 import QtWebEngineWidgets
    WEB_ENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    WEB_ENGINE_AVAILABLE = False

try:
    import vlc
    VLC_AVAILABLE = True
except Exception:
    vlc = None
    VLC_AVAILABLE = False

from data import categories, get_products, get_product_by_id, HOME_VIDEO_URL

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def load_users():
    """Load users from JSON file."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass


def pixmap_for_product(product):
    """Get a QPixmap for a product. Use image_path if available, else generate placeholder."""
    img_path = product.get("image_path")
    if img_path and os.path.exists(img_path):
        return QtGui.QPixmap(img_path)
    
    # Fallback: generate a colored placeholder
    size = QtCore.QSize(200, 200)
    pixmap = QtGui.QPixmap(size)
    pixmap.fill(QtGui.QColor(200, 100, 150))  # Rose-gold placeholder
    return pixmap


class LoginDialog(QtWidgets.QDialog):
    """Login dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JewelMart - Login")
        self.setGeometry(100, 100, 400, 250)
        layout = QtWidgets.QVBoxLayout()
        
        label = QtWidgets.QLabel("Login")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        btn_layout = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        register_btn = QtWidgets.QPushButton("Register")
        login_btn.clicked.connect(self.accept)
        register_btn.clicked.connect(self.reject)
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class RegistrationDialog(QtWidgets.QDialog):
    """Registration dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JewelMart - Register")
        self.setGeometry(100, 100, 400, 300)
        layout = QtWidgets.QVBoxLayout()
        
        label = QtWidgets.QLabel("Register")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)
        
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        self.confirm_password_input = QtWidgets.QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.confirm_password_input)
        
        btn_layout = QtWidgets.QHBoxLayout()
        register_btn = QtWidgets.QPushButton("Register")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        register_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class ProductWidget(QtWidgets.QWidget):
    """Display a single product with image and details."""
    
    clicked = QtCore.pyqtSignal(dict)
    
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        layout = QtWidgets.QVBoxLayout()
        
        # Image
        pixmap = pixmap_for_product(product)
        img_label = QtWidgets.QLabel()
        img_label.setPixmap(pixmap.scaledToHeight(150, QtCore.Qt.SmoothTransformation))
        layout.addWidget(img_label)
        
        # Name
        name = QtWidgets.QLabel(product.get("name", "Product"))
        name.setStyleSheet("font-weight: bold;")
        layout.addWidget(name)
        
        # Price
        price = QtWidgets.QLabel(f"₹ {product.get('price', 0)}")
        layout.addWidget(price)
        
        # Button
        btn = QtWidgets.QPushButton("View Details")
        btn.clicked.connect(self.on_click)
        layout.addWidget(btn)
        
        self.setLayout(layout)
        self.setStyleSheet("border: 1px solid #ccc; padding: 10px; border-radius: 5px;")
    
    def on_click(self):
        self.clicked.emit(self.product)


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart - Jewelry Store")
        self.setGeometry(100, 100, 1200, 700)
        self.current_user = None
        self.cart = []
        self.wishlist = []
        
        # Main widget and stack
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        
        # Navigation bar (will be shown after login)
        self.nav_layout = QtWidgets.QHBoxLayout()
        self.nav_buttons = {}
        main_layout.addLayout(self.nav_layout)
        
        # Page stack
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack, 1)
        
        # Create all pages
        self.login_page = self.create_login()
        self.home_page = self.create_home()
        self.category_page = self.create_category_page()
        self.products_page = self.create_products_page()
        self.product_detail_page = self.create_product_detail()
        self.cart_page = self.create_cart_page()
        self.wishlist_page = self.create_wishlist_page()
        self.contact_page = self.create_contact_page()
        self.about_page = self.create_about_page()
        self.feedback_page = self.create_feedback_page()
        
        # Add pages to stack
        for i, p in enumerate([
            self.login_page,
            self.home_page,
            self.category_page,
            self.products_page,
            self.product_detail_page,
            self.cart_page,
            self.wishlist_page,
            self.contact_page,
            self.about_page,
            self.feedback_page
        ]):
            self.stack.addWidget(p)
        
        self.show_login()
    
    def create_login(self):
        """Create login page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("Welcome to JewelMart")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
        
        login_btn = QtWidgets.QPushButton("Login")
        register_btn = QtWidgets.QPushButton("Register")
        login_btn.clicked.connect(self.show_login_dialog)
        register_btn.clicked.connect(self.show_register_dialog)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        layout.addStretch()
        
        return w
    
    def create_home(self):
        """Create home page with video using QMediaPlayer."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        
        print(f"\n[HOME] ========== HOME PAGE ==========")
        print(f"[HOME] Video: {HOME_VIDEO_URL}")
        
        # Create video widget
        video_widget = QtMultimediaWidgets.QVideoWidget()
        video_widget.setStyleSheet("background-color: black;")
        layout.addWidget(video_widget)
        
        # Create media player
        self.media_player = QtMultimedia.QMediaPlayer()
        self.media_player.setVideoOutput(video_widget)
        
        if HOME_VIDEO_URL and os.path.exists(HOME_VIDEO_URL):
            print(f"[HOME] Setting media: {HOME_VIDEO_URL}")
            
            # Use QUrl to open the video file
            media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL))
            self.media_player.setMedia(media)
            
            # Connect signals
            self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
            self.media_player.stateChanged.connect(self.on_player_state_changed)
            self.media_player.positionChanged.connect(self.on_position_changed)
            self.media_player.durationChanged.connect(self.on_duration_changed)
            
            # Set volume to 0 (muted)
            self.media_player.setVolume(0)
            
            # Play
            print(f"[HOME] Starting playback...")
            self.media_player.play()
        else:
            print(f"[HOME] Video not found, showing welcome screen")
            self.show_welcome_screen(layout)
        
        print(f"[HOME] ========== READY ==========\n")
        return w
    
    def show_welcome_screen(self, layout):
        """Display welcome screen."""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: black;")
        vbox = QtWidgets.QVBoxLayout(widget)
        vbox.addStretch()
        
        title = QtWidgets.QLabel("JewelMart")
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #E6C8D8;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Premium Jewelry Store")
        subtitle.setStyleSheet("font-size: 20px; color: #B8A0B8;")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(subtitle)
        
        vbox.addStretch()
        layout.addWidget(widget, 1)
    
    def on_media_status_changed(self, status):
        """Handle media status changes."""
        status_map = {
            QtMultimedia.QMediaPlayer.UnknownMediaStatus: "Unknown",
            QtMultimedia.QMediaPlayer.NoMedia: "NoMedia",
            QtMultimedia.QMediaPlayer.LoadingMedia: "Loading",
            QtMultimedia.QMediaPlayer.LoadedMedia: "Loaded",
            QtMultimedia.QMediaPlayer.StalledMedia: "Stalled",
            QtMultimedia.QMediaPlayer.BufferingMedia: "Buffering",
            QtMultimedia.QMediaPlayer.BufferedMedia: "Buffered",
            QtMultimedia.QMediaPlayer.EndOfMedia: "EndOfMedia",
            QtMultimedia.QMediaPlayer.InvalidMedia: "InvalidMedia",
        }
        print(f"[HOME] Media status: {status_map.get(status, str(status))}")
        
        # Loop: restart when finished
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            print(f"[HOME] End of video, restarting...")
            self.media_player.setPosition(0)
            self.media_player.play()
    
    def on_player_state_changed(self, state):
        """Handle player state changes."""
        state_map = {
            QtMultimedia.QMediaPlayer.StoppedState: "Stopped",
            QtMultimedia.QMediaPlayer.PlayingState: "Playing",
            QtMultimedia.QMediaPlayer.PausedState: "Paused",
        }
        print(f"[HOME] Player state: {state_map.get(state, str(state))}")
    
    def on_position_changed(self, position):
        """Handle position changes."""
        pass  # Suppress verbose logging
    
    def on_duration_changed(self, duration):
        """Handle duration changes."""
        print(f"[HOME] Video duration: {duration}ms")

    
    def create_category_page(self):
        """Create category selection page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("Categories")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        for cat in categories:
            btn = QtWidgets.QPushButton(cat)
            btn.clicked.connect(lambda checked, c=cat: self.show_products_for_category(c))
            layout.addWidget(btn)
        
        layout.addStretch()
        return w
    
    def create_products_page(self):
        """Create products display page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        grid_widget = QtWidgets.QWidget()
        self.products_grid = QtWidgets.QGridLayout(grid_widget)
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        
        return w
    
    def create_product_detail(self):
        """Create product detail page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        self.detail_image = QtWidgets.QLabel()
        self.detail_name = QtWidgets.QLabel()
        self.detail_price = QtWidgets.QLabel()
        self.detail_desc = QtWidgets.QLabel()
        
        layout.addWidget(self.detail_image)
        layout.addWidget(self.detail_name)
        layout.addWidget(self.detail_price)
        layout.addWidget(self.detail_desc)
        
        btn_layout = QtWidgets.QHBoxLayout()
        cart_btn = QtWidgets.QPushButton("Add to Cart")
        wishlist_btn = QtWidgets.QPushButton("Add to Wishlist")
        tryon_btn = QtWidgets.QPushButton("Try On")
        cart_btn.clicked.connect(self.add_to_cart)
        wishlist_btn.clicked.connect(self.add_to_wishlist)
        tryon_btn.clicked.connect(self.launch_tryon)
        btn_layout.addWidget(cart_btn)
        btn_layout.addWidget(wishlist_btn)
        btn_layout.addWidget(tryon_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        return w
    
    def create_cart_page(self):
        """Create shopping cart page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("Shopping Cart")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        self.cart_list = QtWidgets.QListWidget()
        layout.addWidget(self.cart_list)
        
        checkout_btn = QtWidgets.QPushButton("Checkout")
        checkout_btn.clicked.connect(self.checkout)
        layout.addWidget(checkout_btn)
        
        return w
    
    def create_wishlist_page(self):
        """Create wishlist page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("Wishlist")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        self.wishlist_list = QtWidgets.QListWidget()
        layout.addWidget(self.wishlist_list)
        
        return w
    
    def create_contact_page(self):
        """Create contact page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("Contact Us")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        info = QtWidgets.QLabel("Email: support@jewelmart.com\nPhone: +91-XXXX-XXXX-XX")
        layout.addWidget(info)
        layout.addStretch()
        
        return w
    
    def create_about_page(self):
        """Create about page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("About JewelMart")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        info = QtWidgets.QLabel("JewelMart is a premium jewelry e-commerce platform.")
        layout.addWidget(info)
        layout.addStretch()
        
        return w
    
    def create_feedback_page(self):
        """Create feedback form page."""
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        
        label = QtWidgets.QLabel("Feedback")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        self.feedback_input = QtWidgets.QTextEdit()
        self.feedback_input.setPlaceholderText("Please share your feedback...")
        layout.addWidget(self.feedback_input)
        
        submit_btn = QtWidgets.QPushButton("Submit")
        submit_btn.clicked.connect(self.submit_feedback)
        layout.addWidget(submit_btn)
        
        layout.addStretch()
        return w
    
    def show_login(self):
        """Show login page."""
        self.nav_layout.setVisible(False)
        self.stack.setCurrentIndex(0)
    
    def show_login_dialog(self):
        """Show login dialog."""
        dialog = LoginDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            users = load_users()
            if username in users and users[username] == password:
                self.current_user = username
                self.show_home()
            else:
                QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid credentials.")
    
    def show_register_dialog(self):
        """Show registration dialog."""
        dialog = RegistrationDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            confirm = dialog.confirm_password_input.text()
            if password == confirm:
                users = load_users()
                if username not in users:
                    users[username] = password
                    save_users(users)
                    self.current_user = username
                    self.show_home()
                else:
                    QtWidgets.QMessageBox.warning(self, "Registration Failed", "User already exists.")
            else:
                QtWidgets.QMessageBox.warning(self, "Registration Failed", "Passwords do not match.")
    
    def show_home(self):
        """Show home page and navigation bar."""
        self.create_nav_bar()
        self.nav_layout.setVisible(True)
        self.stack.setCurrentIndex(1)
    
    def create_nav_bar(self):
        """Create navigation bar."""
        # Clear existing buttons
        while self.nav_layout.count():
            self.nav_layout.takeAt(0).widget().deleteLater()
        
        pages = [
            ("Home", 1),
            ("Categories", 2),
            ("Cart", 5),
            ("Wishlist", 6),
            ("Contact", 7),
            ("About", 8),
            ("Feedback", 9),
            ("Logout", -1)
        ]
        
        for name, idx in pages:
            btn = QtWidgets.QPushButton(name)
            if idx == -1:
                btn.clicked.connect(self.logout)
            else:
                btn.clicked.connect(lambda checked, i=idx: self.stack.setCurrentIndex(i))
            self.nav_layout.addWidget(btn)
    
    def show_products_for_category(self, category):
        """Show products for a category."""
        products = get_products(category)
        
        # Clear grid
        while self.products_grid.count():
            self.products_grid.takeAt(0).widget().deleteLater()
        
        # Add product widgets
        for i, product in enumerate(products):
            w = ProductWidget(product)
            w.clicked.connect(self.show_product_detail)
            row = i // 3
            col = i % 3
            self.products_grid.addWidget(w, row, col)
        
        self.stack.setCurrentIndex(3)
    
    def show_product_detail(self, product):
        """Show product detail."""
        self.current_product = product
        self.detail_name.setText(product.get("name", ""))
        self.detail_price.setText(f"₹ {product.get('price', 0)}")
        self.detail_desc.setText(product.get("description", ""))
        
        pixmap = pixmap_for_product(product)
        self.detail_image.setPixmap(pixmap.scaledToHeight(300, QtCore.Qt.SmoothTransformation))
        
        self.stack.setCurrentIndex(4)
    
    def add_to_cart(self):
        """Add current product to cart."""
        if hasattr(self, 'current_product'):
            self.cart.append(self.current_product)
            self.update_cart_view()
            QtWidgets.QMessageBox.information(self, "Success", "Added to cart!")
    
    def add_to_wishlist(self):
        """Add current product to wishlist."""
        if hasattr(self, 'current_product'):
            self.wishlist.append(self.current_product)
            self.update_wishlist_view()
            QtWidgets.QMessageBox.information(self, "Success", "Added to wishlist!")
    
    def update_cart_view(self):
        """Update cart list view."""
        self.cart_list.clear()
        for item in self.cart:
            self.cart_list.addItem(f"{item.get('name')} - ₹ {item.get('price')}")
    
    def update_wishlist_view(self):
        """Update wishlist view."""
        self.wishlist_list.clear()
        for item in self.wishlist:
            self.wishlist_list.addItem(f"{item.get('name')} - ₹ {item.get('price')}")
    
    def checkout(self):
        """Process checkout."""
        if self.cart:
            total = sum(item.get('price', 0) for item in self.cart)
            QtWidgets.QMessageBox.information(self, "Checkout", f"Total: ₹ {total}\nThank you for your purchase!")
            self.cart = []
            self.update_cart_view()
        else:
            QtWidgets.QMessageBox.information(self, "Cart Empty", "Your cart is empty.")
    
    def launch_tryon(self):
        """Launch virtual try-on."""
        if not hasattr(self, 'current_product'):
            return
        
        try:
            # Load tryon module dynamically
            spec = importlib.util.spec_from_file_location(
                "tryon",
                os.path.join(os.path.dirname(__file__), "tryon", "run.py")
            )
            tryon_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tryon_module)
            
            # Call the try-on function
            if hasattr(tryon_module, 'launch'):
                tryon_module.launch(self.current_product)
            elif hasattr(tryon_module, 'run_tryon'):
                tryon_module.run_tryon(self.current_product)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Try-On Failed", f"Could not launch try-on: {str(e)}")
    
    def submit_feedback(self):
        """Submit feedback."""
        feedback = self.feedback_input.toPlainText()
        if feedback:
            QtWidgets.QMessageBox.information(self, "Success", "Thank you for your feedback!")
            self.feedback_input.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Empty Feedback", "Please enter some feedback.")
    
    def logout(self):
        """Logout user."""
        self.current_user = None
        self.cart = []
        self.wishlist = []
        self.show_login()
