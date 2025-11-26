"""Minimal, single clean UI for JewelMart (final).

This file intentionally kept small and deterministic to avoid prior
corruption. It prefers QtWebEngine for HTML5 playback and falls back to
QtMultimedia; it always provides a poster or message when video playback
is not available so the home page is never blank.
"""

#import os
# In your data.py or wherever HOME_VIDEO_URL is defined
import os

# Assuming your video is in a subfolder like assets/
# Get the directory of the current file (data.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Construct the absolute path
HOME_VIDEO_URL = os.path.join(BASE_DIR, "assets", "E:\JM\JewelMart\assets\JewelMart.mp4")

# If the video is in the same directory as data.py:
# HOME_VIDEO_URL = os.path.join(BASE_DIR, "your_video.mp4")

# # Example in data.py or check where it's defined
# import os
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# HOME_VIDEO_URL = os.path.join(BASE_DIR, "assets", "E:\JM\JewelMart\assets\JewelMart.mp4")
# # Add this import
import os 
# Add at the TOP of your main script (e.g., above all imports)
import os
os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'

# ... rest of your imports and code ...
import json
import importlib.util
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets
try:
                player.error.connect(lambda e: show_poster_and_message())
            except Exception:
                try:
                    player.error.connect(show_poster_and_message)
                except Exception:
                    pass
# try:
#     from PyQt5 import QtWebEngineWidgets
#     WEB_ENGINE_AVAILABLE = True
# except Exception:
#     QtWebEngineWidgets = None
#     WEB_ENGINE_AVAILABLE = False

from data import categories, get_products, get_product_by_id, HOME_VIDEO_URL


USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def show_poster_and_message():
    # ... your existing code ...
    pass

try:
    # TEMPORARY DEBUG: Print the error code
    player.error.connect(lambda e: print(f"QMediaPlayer Error: {e.name}"))
    player.error.connect(show_poster_and_message)
except Exception:
    # ...
    pass

def player_error_debug(error_code, player_instance=player):
                print(f"!!! QMediaPlayer Error: {error_code.name} !!!")
                # Attempt to get more detail if available
                print(f"!!! Error String: {player_instance.errorString()} !!!")
                show_poster_and_message()
                
            try:
                # Connect the custom debug function
                player.error.connect(player_error_debug)
            except Exception:
                # Fallback connection if the above fails
                player.error.connect(show_poster_and_message)

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass


def pixmap_for_product(product, size=(120, 120)):
    w, h = size
    img_path = product.get("image_path") if product else None
    if img_path and os.path.exists(img_path):
        p = QtGui.QPixmap(img_path)
        if not p.isNull():
            return p.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    p = QtGui.QPixmap(w, h)
    p.fill(QtGui.QColor("#dcd0c0"))
    return p


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - JewelMart")
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btns = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        reg_btn = QtWidgets.QPushButton("Register")
        btns.addWidget(login_btn)
        btns.addWidget(reg_btn)
        layout.addLayout(btns)
        login_btn.clicked.connect(self.handle_login)
        reg_btn.clicked.connect(self.open_register)
        self.user = None

    def handle_login(self):
        users = load_users()
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        if email and email in users and users[email].get("password") == pwd:
            self.user = users[email]
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login failed", "Invalid email or password")

    def open_register(self):
        dlg = RegistrationDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Registered", "Account created. You can login now.")


class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - JewelMart")
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.name = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Name:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btn = QtWidgets.QPushButton("Create Account")
        btn.clicked.connect(self.create_account)
        layout.addWidget(btn)

    def create_account(self):
        users = load_users()
        email = self.email.text().strip()
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Email required")
            return
        if email in users:
            QtWidgets.QMessageBox.warning(self, "Error", "User already exists")
            return
        users[email] = {"name": self.name.text().strip(), "password": self.password.text().strip()}
        save_users(users)
        self.accept()


class ProductWidget(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(int)

    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        layout = QtWidgets.QHBoxLayout(self)
        pix = pixmap_for_product(product, size=(80, 80))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        layout.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name = QtWidgets.QLabel(product.get("name", ""))
        price = QtWidgets.QLabel(f"₹ {product.get('price',0):,}")
        v.addWidget(name)
        v.addWidget(price)
        layout.addLayout(v)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.product.get('id'))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart")
        self.resize(1000, 700)
        self.user = None
        self.cart = []
        self.wishlist = set()

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # pages
        self.home_page = self.create_home()
        self.category_page = self.create_category_page()
        self.products_page = self.create_products_page()
        self.product_detail_page = self.create_product_detail()
        self.cart_page = self.create_cart_page()
        self.wishlist_page = self.create_wishlist_page()
        self.contact_page = self.create_contact_page()
        self.about_page = self.create_about_page()
        self.feedback_page = self.create_feedback_page()

        for p in [
            self.home_page,
            self.category_page,
            self.products_page,
            self.product_detail_page,
            self.cart_page,
            self.wishlist_page,
            self.contact_page,
            self.about_page,
            self.feedback_page,
        ]:
            self.stack.addWidget(p)

        self.create_menu()
        self.show_login()
        self.show_home()

    def create_menu(self):
        menubar = self.menuBar()
        nav = menubar.addMenu("Navigate")
        nav.addAction("Home", self.show_home)
        nav.addAction("Categories", lambda: self.stack.setCurrentWidget(self.category_page))
        nav.addAction("Cart", self.show_cart)
        nav.addAction("Wishlist", self.show_wishlist)
        nav.addAction("Contact Us", lambda: self.stack.setCurrentWidget(self.contact_page))
        nav.addAction("About Us", lambda: self.stack.setCurrentWidget(self.about_page))
        nav.addAction("Feedback", lambda: self.stack.setCurrentWidget(self.feedback_page))

    def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        if HOME_VIDEO_URL:
            # Try WebEngine HTML5 <video> first when available
            if WEB_ENGINE_AVAILABLE and QtWebEngineWidgets is not None:
                try:
                    view = QtWebEngineWidgets.QWebEngineView()
                    view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                    view.setMinimumSize(640, 360)
                    file_url = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL).toString() if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl(HOME_VIDEO_URL).toString()
                    html = (
                        "<!doctype html><html><head><meta charset='utf-8'></head>"
                        "<body style='margin:0;background:#000;'>"
                        f"<video autoplay loop muted playsinline style='width:100%;height:100%;object-fit:cover;'>"
                        f"<source src='{file_url}' type='video/mp4'>"
                        "Your browser does not support the video tag."
                        "</video></body></html>"
                    )
                    base = QtCore.QUrl.fromLocalFile(os.path.dirname(HOME_VIDEO_URL)) if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl("./")
                    view.setHtml(html, base)
                    layout.addWidget(view, 1)
                    return w
                except Exception:
                    pass

            # QtMultimedia fallback
            video_widget = QtMultimediaWidgets.QVideoWidget()
            # ... (rest of the QtMultimedia fallback code) ...
            
            player.play()
            layout.addWidget(video_widget, 1)
        else:
            # ... (code for when HOME_VIDEO_URL is not set) ...

        return w
    
                except Exception:
                    pass

            # QtMultimedia fallback
            video_widget = QtMultimediaWidgets.QVideoWidget()
            video_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            video_widget.setMinimumSize(640, 360)

            player = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
            playlist = QtMultimedia.QMediaPlaylist()
            if os.path.exists(HOME_VIDEO_URL):
                url_obj = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL)
            else:
                url_obj = QtCore.QUrl(HOME_VIDEO_URL)
            playlist.addMedia(QtMultimedia.QMediaContent(url_obj))
            playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)

            player.setPlaylist(playlist)
            player.setVideoOutput(video_widget)
            try:
                player.setMuted(True)
            except Exception:
                try:
                    player.setVolume(0)
                except Exception:
                    pass

            def show_poster_and_message():
                try:
                    video_widget.hide()
                except Exception:
                    pass
                poster_pix = None
                prods = get_products()
                if prods:
                    poster_pix = pixmap_for_product(prods[0], size=(800, 450))
                if poster_pix is not None:
                    lbl = QtWidgets.QLabel()
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    lbl.setPixmap(poster_pix)
                    layout.addWidget(lbl, 1)
                else:
                    lbl = QtWidgets.QLabel("Video playback unavailable.")
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    layout.addWidget(lbl, 1)
                try:
                    player.stop()
                except Exception:
                    pass

            try:
                player.error.connect(lambda e: show_poster_and_message())
            except Exception:
                try:
                    player.error.connect(show_poster_and_message)
                except Exception:
                    pass

            try:
                def status_changed(status):
                    try:
                        if status == QtMultimedia.QMediaPlayer.InvalidMedia:
                            show_poster_and_message()
                    except Exception:
                        pass
                player.mediaStatusChanged.connect(status_changed)
            except Exception:
                pass

            player.play()
            layout.addWidget(video_widget, 1)
        else:
            header = QtWidgets.QLabel("Welcome to JewelMart")
            header.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(header)
            layout.addWidget(QtWidgets.QLabel("Beautiful jewelry collections. Browse categories and pick your favorite pieces."))

        return w

    # (other page creators and handlers omitted for brevity in this patch)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
"""Minimal clean UI for JewelMart.

This file implements a simple MainWindow where the home page shows a
muted, looping video (HTML5 via QtWebEngine if present) and falls back to
QtMultimedia. When playback fails the page shows a poster image so it's not blank.
"""

import json
import os
import importlib.util
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets

try:
    from PyQt5 import QtWebEngineWidgets
    WEB_ENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    WEB_ENGINE_AVAILABLE = False

from data import categories, get_products, get_product_by_id, HOME_VIDEO_URL


def pixmap_for_product(product, size=(120, 120)):
    w, h = size
    img_path = product.get("image_path")
    if img_path and os.path.exists(img_path):
        p = QtGui.QPixmap(img_path)
        if not p.isNull():
            return p.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    p = QtGui.QPixmap(w, h)
    p.fill(QtGui.QColor("#dcd0c0"))
    return p


USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - JewelMart")
        self.resize(320, 150)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btns = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        reg_btn = QtWidgets.QPushButton("Register")
        btns.addWidget(login_btn)
        btns.addWidget(reg_btn)
        layout.addLayout(btns)
        login_btn.clicked.connect(self.handle_login)
        reg_btn.clicked.connect(self.open_register)
        self.user = None

    def handle_login(self):
        users = load_users()
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        if email and email in users and users[email].get("password") == pwd:
            self.user = users[email]
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login failed", "Invalid email or password")

    def open_register(self):
        dlg = RegistrationDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Registered", "Account created. You can login now.")


class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - JewelMart")
        self.resize(360, 200)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.name = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Name:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btn = QtWidgets.QPushButton("Create Account")
        btn.clicked.connect(self.create_account)
        layout.addWidget(btn)

    def create_account(self):
        users = load_users()
        email = self.email.text().strip()
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Email required")
            return
        if email in users:
            QtWidgets.QMessageBox.warning(self, "Error", "User already exists")
            return
        users[email] = {"name": self.name.text().strip(), "password": self.password.text().strip()}
        save_users(users)
        self.accept()


class ProductWidget(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(int)

    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        layout = QtWidgets.QHBoxLayout(self)
        pix = pixmap_for_product(product, size=(80, 80))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        layout.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name = QtWidgets.QLabel(product.get("name", ""))
        price = QtWidgets.QLabel(f"₹ {product.get('price',0):,}")
        v.addWidget(name)
        v.addWidget(price)
        layout.addLayout(v)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.product.get('id'))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart")
        self.resize(1000, 700)
        self.user = None
        self.cart = []
        self.wishlist = set()

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # pages
        self.home_page = self.create_home()
        self.category_page = self.create_category_page()
        self.products_page = self.create_products_page()
        self.product_detail_page = self.create_product_detail()
        self.cart_page = self.create_cart_page()
        self.wishlist_page = self.create_wishlist_page()
        self.contact_page = self.create_contact_page()
        self.about_page = self.create_about_page()
        self.feedback_page = self.create_feedback_page()

        for p in [
            self.home_page,
            self.category_page,
            self.products_page,
            self.product_detail_page,
            self.cart_page,
            self.wishlist_page,
            self.contact_page,
            self.about_page,
            self.feedback_page,
        ]:
            self.stack.addWidget(p)

        self.create_menu()
        self.show_login()
        self.show_home()

    def create_menu(self):
        menubar = self.menuBar()
        nav = menubar.addMenu("Navigate")
        nav.addAction("Home", self.show_home)
        nav.addAction("Categories", lambda: self.stack.setCurrentWidget(self.category_page))
        nav.addAction("Cart", self.show_cart)
        nav.addAction("Wishlist", self.show_wishlist)
        nav.addAction("Contact Us", lambda: self.stack.setCurrentWidget(self.contact_page))
        nav.addAction("About Us", lambda: self.stack.setCurrentWidget(self.about_page))
        nav.addAction("Feedback", lambda: self.stack.setCurrentWidget(self.feedback_page))

    def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        if HOME_VIDEO_URL:
            # Try WebEngine HTML5 <video> first when available
            if WEB_ENGINE_AVAILABLE and QtWebEngineWidgets is not None:
                try:
                    view = QtWebEngineWidgets.QWebEngineView()
                    view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                    view.setMinimumSize(640, 360)
                    file_url = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL).toString() if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl(HOME_VIDEO_URL).toString()
                    html = (
                        "<!doctype html><html><head><meta charset='utf-8'></head>"
                        "<body style='margin:0;background:#000;'>"
                        f"<video autoplay loop muted playsinline style='width:100%;height:100%;object-fit:cover;'>"
                        f"<source src='{file_url}' type='video/mp4'>"
                        "Your browser does not support the video tag."
                        "</video></body></html>"
                    )
                    base = QtCore.QUrl.fromLocalFile(os.path.dirname(HOME_VIDEO_URL)) if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl("./")
                    view.setHtml(html, base)
                    layout.addWidget(view, 1)
                    return w
                except Exception:
                    pass

            # QtMultimedia fallback
            video_widget = QtMultimediaWidgets.QVideoWidget()
            video_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            video_widget.setMinimumSize(640, 360)

            player = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
            playlist = QtMultimedia.QMediaPlaylist()
            if os.path.exists(HOME_VIDEO_URL):
                url_obj = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL)
            else:
                url_obj = QtCore.QUrl(HOME_VIDEO_URL)
            playlist.addMedia(QtMultimedia.QMediaContent(url_obj))
            playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)

            player.setPlaylist(playlist)
            player.setVideoOutput(video_widget)
            try:
                player.setMuted(True)
            except Exception:
                try:
                    player.setVolume(0)
                except Exception:
                    pass

            def show_poster_and_message():
                try:
                    video_widget.hide()
                except Exception:
                    pass
                poster_pix = None
                prods = get_products()
                if prods:
                    poster_pix = pixmap_for_product(prods[0], size=(800, 450))
                if poster_pix is not None:
                    lbl = QtWidgets.QLabel()
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    lbl.setPixmap(poster_pix)
                    layout.addWidget(lbl, 1)
                else:
                    lbl = QtWidgets.QLabel("Video playback unavailable.")
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    layout.addWidget(lbl, 1)
                try:
                    player.stop()
                except Exception:
                    pass

            try:
                player.error.connect(lambda e: show_poster_and_message())
            except Exception:
                try:
                    player.error.connect(show_poster_and_message)
                except Exception:
                    pass

            try:
                def status_changed(status):
                    try:
                        if status == QtMultimedia.QMediaPlayer.InvalidMedia:
                            show_poster_and_message()
                    except Exception:
                        pass
                player.mediaStatusChanged.connect(status_changed)
            except Exception:
                pass

            player.play()
            layout.addWidget(video_widget, 1)
        else:
            header = QtWidgets.QLabel("Welcome to JewelMart")
            header.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(header)
            layout.addWidget(QtWidgets.QLabel("Beautiful jewelry collections. Browse categories and pick your favorite pieces."))

        return w

    def create_category_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("Categories"))
        btn_layout = QtWidgets.QHBoxLayout()
        for c in categories:
            b = QtWidgets.QPushButton(c)
            b.clicked.connect(lambda _, cat=c: self.open_category(cat))
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        return w

    def create_products_page(self):
        w = QtWidgets.QWidget()
        self.products_layout = QtWidgets.QVBoxLayout()
        sc = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        container.setLayout(self.products_layout)
        sc.setWidget(container)
        sc.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(sc)
        return w

    def create_product_detail(self):
        w = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_cart_page(self):
        w = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_wishlist_page(self):
        w = QtWidgets.QWidget()
        self.wishlist_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_contact_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(w)
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Email:", QtWidgets.QLineEdit())
        layout.addRow("Message:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Send"))
        return w

    def create_about_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("About JewelMart"))
        layout.addWidget(QtWidgets.QLabel("JewelMart is a demo desktop application showcasing jewelry catalogs."))
        return w

    def create_feedback_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(w)
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Rating (1-5):", QtWidgets.QSpinBox())
        layout.addRow("Comments:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Submit"))
        return w

    def show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.user = dlg.user
            self.statusBar().showMessage(f"Logged in as {self.user.get('name','')}")

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_category(self, cat):
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        prods = get_products(cat)
        for p in prods:
            pw = ProductWidget(p)
            pw.clicked.connect(self.open_product)
            self.products_layout.addWidget(pw)
        self.stack.setCurrentWidget(self.products_page)

    def open_product(self, pid):
        prod = get_product_by_id(pid)
        if not prod:
            return
        for i in reversed(range(self.detail_layout.count())):
            item = self.detail_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        h = QtWidgets.QHBoxLayout()
        pix = pixmap_for_product(prod, size=(240, 240))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        h.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name_lbl = QtWidgets.QLabel(prod['name'])
        price_lbl = QtWidgets.QLabel(f"Price: ₹ {prod['price']:,}")
        v.addWidget(name_lbl)
        v.addWidget(price_lbl)
        v.addWidget(QtWidgets.QLabel(prod.get('description', '')))
        wish_btn = QtWidgets.QPushButton("Add to Wishlist")
        cart_btn = QtWidgets.QPushButton("Add to Cart")
        tryon_btn = QtWidgets.QPushButton("Virtual Try-On")
        wish_btn.clicked.connect(lambda _, pid=pid: self.add_to_wishlist(pid))
        cart_btn.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
        tryon_btn.clicked.connect(lambda _, pid=pid: self.virtual_tryon(pid))
        v.addWidget(wish_btn)
        v.addWidget(cart_btn)
        v.addWidget(tryon_btn)
        h.addLayout(v)
        self.detail_layout.addLayout(h)
        self.stack.setCurrentWidget(self.product_detail_page)

    def add_to_wishlist(self, pid):
        self.wishlist.add(pid)
        QtWidgets.QMessageBox.information(self, "Wishlist", "Added to wishlist")

    def add_to_cart(self, pid):
        self.cart.append(pid)
        QtWidgets.QMessageBox.information(self, "Cart", "Added to cart")

    def virtual_tryon(self, pid):
        base = os.path.dirname(__file__)
        tryon_folder = os.path.join(base, "tryon")
        candidates = [
            os.path.join(tryon_folder, "run.py"),
            os.path.join(tryon_folder, "__init__.py"),
            os.path.join(base, "tryon.py"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    spec = importlib.util.spec_from_file_location("jewel_tryon", c)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "launch"):
                        mod.launch(get_product_by_id(pid))
                        return
                    if hasattr(mod, "run_tryon"):
                        mod.run_tryon(get_product_by_id(pid))
                        return
                    if hasattr(mod, "main"):
                        mod.main(get_product_by_id(pid))
                        return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Try-On Error", f"Error launching try-on: {e}")
                    return
        QtWidgets.QMessageBox.information(self, "Virtual Try-On", "No try-on module found.")

    def show_cart(self):
        for i in reversed(range(self.cart_layout.count())):
            item = self.cart_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        total = 0
        for pid in self.cart:
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"₹ {p['price']:,}"))
            remove = QtWidgets.QPushButton("Remove")
            remove.clicked.connect(lambda _, pid=pid: self.remove_from_cart(pid))
            row.addWidget(remove)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.cart_layout.addWidget(container)
            total += p['price']
        self.cart_layout.addWidget(QtWidgets.QLabel(f"Total: ₹ {total:,}"))
        pay_btn = QtWidgets.QPushButton("Checkout / Pay")
        pay_btn.clicked.connect(self.checkout)
        self.cart_layout.addWidget(pay_btn)
        self.stack.setCurrentWidget(self.cart_page)

    def remove_from_cart(self, pid):
        self.cart = [x for x in self.cart if x != pid]
        self.show_cart()

    def checkout(self):
        if not self.cart:
            QtWidgets.QMessageBox.information(self, "Checkout", "Your cart is empty")
            return
        total = sum(get_product_by_id(pid)['price'] for pid in self.cart)
        modes = ("Cash on Delivery", "Card", "UPI")
        mode, ok = QtWidgets.QInputDialog.getItem(self, "Payment", f"Total: ₹ {total}\nChoose payment mode:", modes, 0, False)
        if ok:
            QtWidgets.QMessageBox.information(self, "Paid", f"Payment mode: {mode}\nAmount: ₹ {total}\nThank you for your purchase!")
            self.cart = []
            self.show_cart()

    def show_wishlist(self):
        for i in reversed(range(self.wishlist_layout.count())):
            item = self.wishlist_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for pid in list(self.wishlist):
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"₹ {p['price']:,}"))
            add_cart = QtWidgets.QPushButton("Add to Cart")
            add_cart.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
            row.addWidget(add_cart)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.wishlist_layout.addWidget(container)
        self.stack.setCurrentWidget(self.wishlist_page)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
# Clean single-file UI implementation: prefer WebEngine, fall back to QtMultimedia
import json
import os
import importlib.util
from PyQt5 import QtWidgets, QtGui, QtCore
"""
Minimal clean UI module for JewelMart.

Behavior:
- Prefers QtWebEngine HTML5 <video> for the home page if available.
- Falls back to QtMultimedia QMediaPlayer with a poster/error fallback when WebEngine is not present or fails.
"""

import json
import os
import importlib.util
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets

try:
    from PyQt5 import QtWebEngineWidgets
    WEB_ENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    WEB_ENGINE_AVAILABLE = False

from data import categories, get_products, get_product_by_id, HOME_VIDEO_URL

def pixmap_for_product(product, size=(120, 120)):
    w, h = size
    img_path = product.get("image_path")
    if img_path and os.path.exists(img_path):
        p = QtGui.QPixmap(img_path)
        if not p.isNull():
            return p.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    p = QtGui.QPixmap(w, h)
    p.fill(QtGui.QColor("#dcd0c0"))
    return p

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - JewelMart")
        self.resize(320, 150)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btns = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        reg_btn = QtWidgets.QPushButton("Register")
        btns.addWidget(login_btn)
        btns.addWidget(reg_btn)
        layout.addLayout(btns)
        login_btn.clicked.connect(self.handle_login)
        reg_btn.clicked.connect(self.open_register)
        self.user = None

    def handle_login(self):
        users = load_users()
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        if email and email in users and users[email].get("password") == pwd:
            self.user = users[email]
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login failed", "Invalid email or password")

    def open_register(self):
        dlg = RegistrationDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Registered", "Account created. You can login now.")

class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - JewelMart")
        self.resize(360, 200)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.name = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Name:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btn = QtWidgets.QPushButton("Create Account")
        btn.clicked.connect(self.create_account)
        layout.addWidget(btn)

    def create_account(self):
        users = load_users()
        email = self.email.text().strip()
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Email required")
            return
        if email in users:
            QtWidgets.QMessageBox.warning(self, "Error", "User already exists")
            return
        users[email] = {"name": self.name.text().strip(), "password": self.password.text().strip()}
        save_users(users)
        self.accept()

class ProductWidget(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(int)

    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        layout = QtWidgets.QHBoxLayout(self)
        pix = pixmap_for_product(product, size=(80, 80))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        layout.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name = QtWidgets.QLabel(product.get("name", ""))
        price = QtWidgets.QLabel(f"₹ {product.get('price',0):,}")
        v.addWidget(name)
        v.addWidget(price)
        layout.addLayout(v)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.product.get('id'))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JewelMart")
        self.resize(1000, 700)
        self.user = None
        self.cart = []
        self.wishlist = set()
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # pages
        self.home_page = self.create_home()
        self.category_page = self.create_category_page()
        self.products_page = self.create_products_page()
        self.product_detail_page = self.create_product_detail()
        self.cart_page = self.create_cart_page()
        self.wishlist_page = self.create_wishlist_page()
        self.contact_page = self.create_contact_page()
        self.about_page = self.create_about_page()
        self.feedback_page = self.create_feedback_page()

        for p in [
            self.home_page,
            self.category_page,
            self.products_page,
            self.product_detail_page,
            self.cart_page,
            self.wishlist_page,
            self.contact_page,
            self.about_page,
            self.feedback_page,
        ]:
            self.stack.addWidget(p)

        self.create_menu()
        self.show_login()
        self.show_home()

    def create_menu(self):
        menubar = self.menuBar()
        nav = menubar.addMenu("Navigate")
        nav.addAction("Home", self.show_home)
        nav.addAction("Categories", lambda: self.stack.setCurrentWidget(self.category_page))
        nav.addAction("Cart", self.show_cart)
        nav.addAction("Wishlist", self.show_wishlist)
        nav.addAction("Contact Us", lambda: self.stack.setCurrentWidget(self.contact_page))
        nav.addAction("About Us", lambda: self.stack.setCurrentWidget(self.about_page))
        nav.addAction("Feedback", lambda: self.stack.setCurrentWidget(self.feedback_page))

    def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        if HOME_VIDEO_URL:
            # WebEngine HTML5 <video> first
            if WEB_ENGINE_AVAILABLE and QtWebEngineWidgets is not None:
                try:
                    view = QtWebEngineWidgets.QWebEngineView()
                    view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                    view.setMinimumSize(640, 360)
                    if os.path.exists(HOME_VIDEO_URL):
                        file_url = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL).toString()
                    else:
                        file_url = QtCore.QUrl(HOME_VIDEO_URL).toString()
                    html = (
                        "<!doctype html><html><head><meta charset='utf-8'></head>"
                        "<body style='margin:0;background:#000;'>"
                        f"<video autoplay loop muted playsinline style='width:100%;height:100%;object-fit:cover;'>"
                        f"<source src='{file_url}' type='video/mp4'>"
                        "Your browser does not support the video tag."
                        "</video></body></html>"
                    )
                    base = QtCore.QUrl.fromLocalFile(os.path.dirname(HOME_VIDEO_URL)) if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl("./")
                    view.setHtml(html, base)
                    layout.addWidget(view, 1)
                    return w
                except Exception:
                    pass

            # QtMultimedia fallback
            video_widget = QtMultimediaWidgets.QVideoWidget()
            video_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            video_widget.setMinimumSize(640, 360)

            player = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
            playlist = QtMultimedia.QMediaPlaylist()
            if os.path.exists(HOME_VIDEO_URL):
                url_obj = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL)
            else:
                url_obj = QtCore.QUrl(HOME_VIDEO_URL)
            playlist.addMedia(QtMultimedia.QMediaContent(url_obj))
            playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)

            player.setPlaylist(playlist)
            player.setVideoOutput(video_widget)
            try:
                player.setMuted(True)
            except Exception:
                try:
                    player.setVolume(0)
                except Exception:
                    pass

            def show_poster_and_message():
                try:
                    video_widget.hide()
                except Exception:
                    pass
                poster_pix = None
                prods = get_products()
                if prods:
                    poster_pix = pixmap_for_product(prods[0], size=(800, 450))
                if poster_pix is not None:
                    lbl = QtWidgets.QLabel()
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    lbl.setPixmap(poster_pix)
                    layout.addWidget(lbl, 1)
                else:
                    lbl = QtWidgets.QLabel("Video playback unavailable.")
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    layout.addWidget(lbl, 1)
                try:
                    player.stop()
                except Exception:
                    pass

            try:
                player.error.connect(lambda e: show_poster_and_message())
            except Exception:
                try:
                    player.error.connect(show_poster_and_message)
                except Exception:
                    pass

            try:
                def status_changed(status):
                    try:
                        if status == QtMultimedia.QMediaPlayer.InvalidMedia:
                            show_poster_and_message()
                    except Exception:
                        pass
                player.mediaStatusChanged.connect(status_changed)
            except Exception:
                pass

            player.play()
            layout.addWidget(video_widget, 1)
        else:
            header = QtWidgets.QLabel("Welcome to JewelMart")
            header.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(header)
            layout.addWidget(QtWidgets.QLabel("Beautiful jewelry collections. Browse categories and pick your favorite pieces."))

        return w

    def create_category_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("Categories"))
        btn_layout = QtWidgets.QHBoxLayout()
        for c in categories:
            b = QtWidgets.QPushButton(c)
            b.clicked.connect(lambda _, cat=c: self.open_category(cat))
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        return w

    def create_products_page(self):
        w = QtWidgets.QWidget()
        self.products_layout = QtWidgets.QVBoxLayout()
        sc = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        container.setLayout(self.products_layout)
        sc.setWidget(container)
        sc.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(sc)
        return w

    def create_product_detail(self):
        w = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_cart_page(self):
        w = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_wishlist_page(self):
        w = QtWidgets.QWidget()
        self.wishlist_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_contact_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(w)
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Email:", QtWidgets.QLineEdit())
        layout.addRow("Message:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Send"))
        return w

    def create_about_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("About JewelMart"))
        layout.addWidget(QtWidgets.QLabel("JewelMart is a demo desktop application showcasing jewelry catalogs."))
        return w

    def create_feedback_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(w)
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Rating (1-5):", QtWidgets.QSpinBox())
        layout.addRow("Comments:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Submit"))
        return w

    def show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.user = dlg.user
            self.statusBar().showMessage(f"Logged in as {self.user.get('name','')}")

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_category(self, cat):
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        prods = get_products(cat)
        for p in prods:
            pw = ProductWidget(p)
            pw.clicked.connect(self.open_product)
            self.products_layout.addWidget(pw)
        self.stack.setCurrentWidget(self.products_page)

    def open_product(self, pid):
        prod = get_product_by_id(pid)
        if not prod:
            return
        for i in reversed(range(self.detail_layout.count())):
            item = self.detail_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        h = QtWidgets.QHBoxLayout()
        pix = pixmap_for_product(prod, size=(240, 240))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        h.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name_lbl = QtWidgets.QLabel(prod['name'])
        price_lbl = QtWidgets.QLabel(f"Price: ₹ {prod['price']:,}")
        v.addWidget(name_lbl)
        v.addWidget(price_lbl)
        v.addWidget(QtWidgets.QLabel(prod.get('description', '')))
        wish_btn = QtWidgets.QPushButton("Add to Wishlist")
        cart_btn = QtWidgets.QPushButton("Add to Cart")
        tryon_btn = QtWidgets.QPushButton("Virtual Try-On")
        wish_btn.clicked.connect(lambda _, pid=pid: self.add_to_wishlist(pid))
        cart_btn.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
        tryon_btn.clicked.connect(lambda _, pid=pid: self.virtual_tryon(pid))
        v.addWidget(wish_btn)
        v.addWidget(cart_btn)
        v.addWidget(tryon_btn)
        h.addLayout(v)
        self.detail_layout.addLayout(h)
        self.stack.setCurrentWidget(self.product_detail_page)

    def add_to_wishlist(self, pid):
        self.wishlist.add(pid)
        QtWidgets.QMessageBox.information(self, "Wishlist", "Added to wishlist")

    def add_to_cart(self, pid):
        self.cart.append(pid)
        QtWidgets.QMessageBox.information(self, "Cart", "Added to cart")

    def virtual_tryon(self, pid):
        base = os.path.dirname(__file__)
        tryon_folder = os.path.join(base, "tryon")
        candidates = [
            os.path.join(tryon_folder, "run.py"),
            os.path.join(tryon_folder, "__init__.py"),
            os.path.join(base, "tryon.py"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    spec = importlib.util.spec_from_file_location("jewel_tryon", c)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "launch"):
                        mod.launch(get_product_by_id(pid))
                        return
                    if hasattr(mod, "run_tryon"):
                        mod.run_tryon(get_product_by_id(pid))
                        return
                    if hasattr(mod, "main"):
                        mod.main(get_product_by_id(pid))
                        return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Try-On Error", f"Error launching try-on: {e}")
                    return
        QtWidgets.QMessageBox.information(self, "Virtual Try-On", "No try-on module found.")

    def show_cart(self):
        for i in reversed(range(self.cart_layout.count())):
            item = self.cart_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        total = 0
        for pid in self.cart:
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"₹ {p['price']:,}"))
            remove = QtWidgets.QPushButton("Remove")
            remove.clicked.connect(lambda _, pid=pid: self.remove_from_cart(pid))
            row.addWidget(remove)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.cart_layout.addWidget(container)
            total += p['price']
        self.cart_layout.addWidget(QtWidgets.QLabel(f"Total: ₹ {total:,}"))
        pay_btn = QtWidgets.QPushButton("Checkout / Pay")
        pay_btn.clicked.connect(self.checkout)
        self.cart_layout.addWidget(pay_btn)
        self.stack.setCurrentWidget(self.cart_page)

    def remove_from_cart(self, pid):
        self.cart = [x for x in self.cart if x != pid]
        self.show_cart()

    def checkout(self):
        if not self.cart:
            QtWidgets.QMessageBox.information(self, "Checkout", "Your cart is empty")
            return
        total = sum(get_product_by_id(pid)['price'] for pid in self.cart)
        modes = ("Cash on Delivery", "Card", "UPI")
        mode, ok = QtWidgets.QInputDialog.getItem(self, "Payment", f"Total: ₹ {total}\nChoose payment mode:", modes, 0, False)
        if ok:
            QtWidgets.QMessageBox.information(self, "Paid", f"Payment mode: {mode}\nAmount: ₹ {total}\nThank you for your purchase!")
            self.cart = []
            self.show_cart()

    def show_wishlist(self):
        for i in reversed(range(self.wishlist_layout.count())):
            item = self.wishlist_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for pid in list(self.wishlist):
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"₹ {p['price']:,}"))
            add_cart = QtWidgets.QPushButton("Add to Cart")
            add_cart.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
            row.addWidget(add_cart)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.wishlist_layout.addWidget(container)
        self.stack.setCurrentWidget(self.wishlist_page)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

# Try WebEngine (HTML5 video) first; fall back to QtMultimedia if unavailable
try:
    from PyQt5 import QtWebEngineWidgets
    WEB_ENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    WEB_ENGINE_AVAILABLE = False

from data import categories, get_products, get_product_by_id, HOME_VIDEO_URL
import importlib.util


def pixmap_for_product(product, size=(120, 120)):
    w, h = size
    img_path = product.get("image_path")
    if img_path and os.path.exists(img_path):
        p = QtGui.QPixmap(img_path)
        if not p.isNull():
            return p.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    p = QtGui.QPixmap(w, h)
    p.fill(QtGui.QColor("#dcd0c0"))
    return p


USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - JewelMart")
        self.resize(320, 150)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btns = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        reg_btn = QtWidgets.QPushButton("Register")
        btns.addWidget(login_btn)
        btns.addWidget(reg_btn)
        layout.addLayout(btns)
        login_btn.clicked.connect(self.handle_login)
        reg_btn.clicked.connect(self.open_register)
        self.user = None

    def handle_login(self):
        users = load_users()
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        if email and email in users and users[email].get("password") == pwd:
            self.user = users[email]
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login failed", "Invalid email or password")

    def open_register(self):
        dlg = RegistrationDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Registered", "Account created. You can login now.")


class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - JewelMart")
        self.resize(360, 200)
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.name = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Name:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btn = QtWidgets.QPushButton("Create Account")
        btn.clicked.connect(self.create_account)
        layout.addWidget(btn)
            self.contact_page,
            self.about_page,
            self.feedback_page,
        ]:
            self.stack.addWidget(p)

        self.create_menu()
        self.show_login()
        self.show_home()

    def create_menu(self):
        menubar = self.menuBar()
        nav = menubar.addMenu("Navigate")
        nav.addAction("Home", self.show_home)
        nav.addAction("Categories", lambda: self.stack.setCurrentWidget(self.category_page))
        nav.addAction("Cart", self.show_cart)
        nav.addAction("Wishlist", self.show_wishlist)
        nav.addAction("Contact Us", lambda: self.stack.setCurrentWidget(self.contact_page))
        nav.addAction("About Us", lambda: self.stack.setCurrentWidget(self.about_page))
        nav.addAction("Feedback", lambda: self.stack.setCurrentWidget(self.feedback_page))

    def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        # show only the video when configured
        if HOME_VIDEO_URL:
            # Preferred method: use QtWebEngine (HTML5 <video>) if available — more robust on Windows
            if HAVE_WEBENGINE and QtWebEngineWidgets is not None:
                try:
                    view = QtWebEngineWidgets.QWebEngineView()
                    # build a minimal HTML wrapper that autoplays, loops, and is muted
                    if os.path.exists(HOME_VIDEO_URL):
                        file_url = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL).toString()
                    else:
                        file_url = QtCore.QUrl(HOME_VIDEO_URL).toString()
                    html = (
                        "<!doctype html><html><head><meta charset='utf-8'></head>"
                        "<body style='margin:0;background:#000;'>"
                        f"<video src='{file_url}' autoplay loop muted playsinline style='width:100%;height:100%;object-fit:contain;'></video>"
                        "</body></html>"
                    )
                    # set baseUrl so relative resources (none here) resolve; use file URL as base
                    base = QtCore.QUrl.fromLocalFile(os.path.dirname(HOME_VIDEO_URL)) if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl("./")
                    view.setHtml(html, base)
                    layout.addWidget(view, 1)
                    return w
                except Exception:
                    # if web engine fails, fall back to QtMultimedia below
                    pass

            # Fallback: use QtMultimedia (existing approach) with poster/error display
            video_widget = QtMultimediaWidgets.QVideoWidget()
            video_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            video_widget.setMinimumSize(640, 360)

            player = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
            playlist = QtMultimedia.QMediaPlaylist()
            if os.path.exists(HOME_VIDEO_URL):
                url_obj = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL)
            else:
                url_obj = QtCore.QUrl(HOME_VIDEO_URL)
            playlist.addMedia(QtMultimedia.QMediaContent(url_obj))
            playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)

            player.setPlaylist(playlist)
            player.setVideoOutput(video_widget)
            try:
                player.setMuted(True)
            except Exception:
                try:
                    player.setVolume(0)
                except Exception:
                    pass

            # Fallback displayed if playback fails
            def show_poster_and_message():
                try:
                    video_widget.hide()
                except Exception:
                    pass
                poster_pix = None
                prods = get_products()
                if prods:
                    poster_pix = pixmap_for_product(prods[0], size=(800, 450))
                if poster_pix is not None:
                    lbl = QtWidgets.QLabel()
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    lbl.setPixmap(poster_pix)
                    layout.addWidget(lbl, 1)
                else:
                    lbl = QtWidgets.QLabel("Video playback unavailable.")
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    layout.addWidget(lbl, 1)
                try:
                    player.stop()
                except Exception:
                    pass

            try:
                player.error.connect(lambda e: show_poster_and_message())
            except Exception:
                try:
                    player.error.connect(show_poster_and_message)
                except Exception:
                    pass

            try:
                def status_changed(status):
                    try:
                        if status == QtMultimedia.QMediaPlayer.InvalidMedia:
                            show_poster_and_message()
                    except Exception:
                        pass
                player.mediaStatusChanged.connect(status_changed)
            except Exception:
                pass

            player.play()
            layout.addWidget(video_widget, 1)
        else:
            header = QtWidgets.QLabel("Welcome to JewelMart")
            header.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(header)
            layout.addWidget(QtWidgets.QLabel("Beautiful jewelry collections. Browse categories and pick your favorite pieces."))

        return w

    def create_category_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("Categories"))
        btn_layout = QtWidgets.QHBoxLayout()
        for c in categories:
            b = QtWidgets.QPushButton(c)
            b.clicked.connect(lambda _, cat=c: self.open_category(cat))
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        return w

    def create_products_page(self):
        w = QtWidgets.QWidget()
        self.products_layout = QtWidgets.QVBoxLayout()
        sc = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        container.setLayout(self.products_layout)
        sc.setWidget(container)
        sc.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(sc)
        return w

    def create_product_detail(self):
        w = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_cart_page(self):
        w = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_wishlist_page(self):
        w = QtWidgets.QWidget()
        self.wishlist_layout = QtWidgets.QVBoxLayout(w)
        return w

    def create_contact_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(w)
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Email:", QtWidgets.QLineEdit())
        layout.addRow("Message:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Send"))
        return w

    def create_about_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(QtWidgets.QLabel("About JewelMart"))
        layout.addWidget(QtWidgets.QLabel("JewelMart is a demo desktop application showcasing jewelry catalogs."))
        return w

    def create_feedback_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(w)
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Rating (1-5):", QtWidgets.QSpinBox())
        layout.addRow("Comments:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Submit"))
        return w

    def show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.user = dlg.user
            self.statusBar().showMessage(f"Logged in as {self.user.get('name','')}")

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_category(self, cat):
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        prods = get_products(cat)
        for p in prods:
            pw = ProductWidget(p)
            pw.clicked.connect(self.open_product)
            self.products_layout.addWidget(pw)
        self.stack.setCurrentWidget(self.products_page)

    def open_product(self, pid):
        prod = get_product_by_id(pid)
        if not prod:
            return
        for i in reversed(range(self.detail_layout.count())):
            item = self.detail_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        h = QtWidgets.QHBoxLayout()
        pix = pixmap_for_product(prod, size=(240, 240))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        h.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name_lbl = QtWidgets.QLabel(prod['name'])
        price_lbl = QtWidgets.QLabel(f"Price: ₹ {prod['price']:,}")
        v.addWidget(name_lbl)
        v.addWidget(price_lbl)
        v.addWidget(QtWidgets.QLabel(prod.get('description', '')))
        wish_btn = QtWidgets.QPushButton("Add to Wishlist")
        cart_btn = QtWidgets.QPushButton("Add to Cart")
        tryon_btn = QtWidgets.QPushButton("Virtual Try-On")
        wish_btn.clicked.connect(lambda _, pid=pid: self.add_to_wishlist(pid))
        cart_btn.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
        tryon_btn.clicked.connect(lambda _, pid=pid: self.virtual_tryon(pid))
        v.addWidget(wish_btn)
        v.addWidget(cart_btn)
        v.addWidget(tryon_btn)
        h.addLayout(v)
        self.detail_layout.addLayout(h)
        self.stack.setCurrentWidget(self.product_detail_page)

    def add_to_wishlist(self, pid):
        self.wishlist.add(pid)
        QtWidgets.QMessageBox.information(self, "Wishlist", "Added to wishlist")

    def add_to_cart(self, pid):
        self.cart.append(pid)
        QtWidgets.QMessageBox.information(self, "Cart", "Added to cart")

    def virtual_tryon(self, pid):
        base = os.path.dirname(__file__)
        tryon_folder = os.path.join(base, "tryon")
        candidates = [
            os.path.join(tryon_folder, "run.py"),
            os.path.join(tryon_folder, "__init__.py"),
            os.path.join(base, "tryon.py"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    spec = importlib.util.spec_from_file_location("jewel_tryon", c)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "launch"):
                        mod.launch(get_product_by_id(pid))
                        return
                    if hasattr(mod, "run_tryon"):
                        mod.run_tryon(get_product_by_id(pid))
                        return
                    if hasattr(mod, "main"):
                        mod.main(get_product_by_id(pid))
                        return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Try-On Error", f"Error launching try-on: {e}")
                    return
        QtWidgets.QMessageBox.information(self, "Virtual Try-On", "No try-on module found.")

    def show_cart(self):
        for i in reversed(range(self.cart_layout.count())):
            item = self.cart_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        total = 0
        for pid in self.cart:
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"₹ {p['price']:,}"))
            remove = QtWidgets.QPushButton("Remove")
            remove.clicked.connect(lambda _, pid=pid: self.remove_from_cart(pid))
            row.addWidget(remove)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.cart_layout.addWidget(container)
            total += p['price']
        self.cart_layout.addWidget(QtWidgets.QLabel(f"Total: ₹ {total:,}"))
        pay_btn = QtWidgets.QPushButton("Checkout / Pay")
        pay_btn.clicked.connect(self.checkout)
        self.cart_layout.addWidget(pay_btn)
        self.stack.setCurrentWidget(self.cart_page)

    def remove_from_cart(self, pid):
        self.cart = [x for x in self.cart if x != pid]
        self.show_cart()

    def checkout(self):
        if not self.cart:
            QtWidgets.QMessageBox.information(self, "Checkout", "Your cart is empty")
            return
        total = sum(get_product_by_id(pid)['price'] for pid in self.cart)
        modes = ("Cash on Delivery", "Card", "UPI")
        mode, ok = QtWidgets.QInputDialog.getItem(self, "Payment", f"Total: ₹ {total}\nChoose payment mode:", modes, 0, False)
        if ok:
            QtWidgets.QMessageBox.information(self, "Paid", f"Payment mode: {mode}\nAmount: ₹ {total}\nThank you for your purchase!")
            self.cart = []
            self.show_cart()

    def show_wishlist(self):
        for i in reversed(range(self.wishlist_layout.count())):
            item = self.wishlist_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for pid in list(self.wishlist):
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"₹ {p['price']:,}"))
            add_cart = QtWidgets.QPushButton("Add to Cart")
            add_cart.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
            row.addWidget(add_cart)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.wishlist_layout.addWidget(container)
        self.stack.setCurrentWidget(self.wishlist_page)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

    # The following methods create pages. They are implemented as helper methods
    # named with a leading underscore to avoid accidental external calls.
    def _create_category_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Categories"))
        btn_layout = QtWidgets.QHBoxLayout()
        for c in categories:
            b = QtWidgets.QPushButton(c)
            b.clicked.connect(lambda _, cat=c: self.open_category(cat))
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        w.setLayout(layout)
        return w

    def _create_products_page(self):
        w = QtWidgets.QWidget()
        self.products_layout = QtWidgets.QVBoxLayout()
        sc = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        container.setLayout(self.products_layout)
        sc.setWidget(container)
        sc.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(sc)
        w.setLayout(layout)
        return w

    def _create_product_detail(self):
        w = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout()
        w.setLayout(self.detail_layout)
        return w

    def _create_cart_page(self):
        w = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout()
        w.setLayout(self.cart_layout)
        return w

    def _create_wishlist_page(self):
        w = QtWidgets.QWidget()
        self.wishlist_layout = QtWidgets.QVBoxLayout()
        w.setLayout(self.wishlist_layout)
        return w

    def _create_contact_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Email:", QtWidgets.QLineEdit())
        layout.addRow("Message:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Send"))
        w.setLayout(layout)
        return w

    def _create_about_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("About JewelMart"))
        layout.addWidget(QtWidgets.QLabel("JewelMart is a demo desktop application showcasing jewelry catalogs."))
        w.setLayout(layout)
        return w

    def _create_feedback_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Rating (1-5):", QtWidgets.QSpinBox())
        layout.addRow("Comments:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Submit"))
        w.setLayout(layout)
        return w

    def show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.user = dlg.user
            self.statusBar().showMessage(f"Logged in as {self.user.get('name','')}")

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_category(self, cat):
        # populate products layout
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        prods = get_products(cat)
        for p in prods:
            pw = ProductWidget(p)
            pw.clicked.connect(self.open_product)
            self.products_layout.addWidget(pw)
        self.stack.setCurrentWidget(self.products_page)

    def open_product(self, pid):
        prod = get_product_by_id(pid)
        if not prod:
            return
        # clear detail
        for i in reversed(range(self.detail_layout.count())):
            item = self.detail_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        h = QtWidgets.QHBoxLayout()
        pix = pixmap_for_product(prod, size=(240, 240))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        h.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name_lbl = QtWidgets.QLabel(prod['name'])
        name_lbl.setProperty("role", "productName")
        price_lbl = QtWidgets.QLabel(f"Price: ₹ {prod['price']:,}")
        price_lbl.setProperty("role", "productPrice")
        v.addWidget(name_lbl)
        v.addWidget(price_lbl)
        v.addWidget(QtWidgets.QLabel(prod.get('description','')))
        wish_btn = QtWidgets.QPushButton("Add to Wishlist")
        cart_btn = QtWidgets.QPushButton("Add to Cart")
        tryon_btn = QtWidgets.QPushButton("Virtual Try-On")
        wish_btn.clicked.connect(lambda _, pid=pid: self.add_to_wishlist(pid))
        cart_btn.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
        tryon_btn.clicked.connect(lambda _, pid=pid: self.virtual_tryon(pid))
        v.addWidget(wish_btn)
        v.addWidget(cart_btn)
        v.addWidget(tryon_btn)
        h.addLayout(v)
        self.detail_layout.addLayout(h)
        self.stack.setCurrentWidget(self.product_detail_page)

    def add_to_wishlist(self, pid):
        self.wishlist.add(pid)
        QtWidgets.QMessageBox.information(self, "Wishlist", "Added to wishlist")

    def add_to_cart(self, pid):
        self.cart.append(pid)
        QtWidgets.QMessageBox.information(self, "Cart", "Added to cart")

    def virtual_tryon(self, pid):
        prod = get_product_by_id(pid)
        # Try to find a try-on module at JewelMart/tryon/run.py or JewelMart/tryon.py
        base = os.path.dirname(__file__)
        tryon_folder = os.path.join(base, "tryon")
        candidates = [
            os.path.join(tryon_folder, "run.py"),
            os.path.join(tryon_folder, "__init__.py"),
            os.path.join(base, "tryon.py"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    spec = importlib.util.spec_from_file_location("jewel_tryon", c)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "launch"):
                        mod.launch(prod)
                        return
                    if hasattr(mod, "run_tryon"):
                        mod.run_tryon(prod)
                        return
                    if hasattr(mod, "main"):
                        mod.main(prod)
                        return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Try-On Error", f"Error launching try-on: {e}")
                    return
        QtWidgets.QMessageBox.information(
            self,
            "Virtual Try-On",
            "No try-on module found. To enable virtual try-on, place your try-on folder at:\n"
            + os.path.join(base, "tryon")
            + "\nwith an entry file `run.py` exposing one of: launch(product), run_tryon(product) or main(product).",
        )

    def toggle_theme(self):
        settings = {"theme": "light"}
        try:
            if hasattr(self, "_load_settings"):
                settings = self._load_settings() or settings
            else:
                settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
        except Exception:
            settings = {"theme": "light"}
        new_theme = "light" if settings.get("theme") == "light" else "dark"
        settings["theme"] = new_theme
        try:
            if hasattr(self, "_save_settings"):
                self._save_settings(settings)
            else:
                settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)
        except Exception:
            pass
        try:
            qss_name = "style.qss" if new_theme == "dark" else "style_light.qss"
            qss_path = os.path.join(os.path.dirname(__file__), qss_name)
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    QtWidgets.QApplication.instance().setStyleSheet(f.read())
        except Exception:
            pass

    def show_cart(self):
        for i in reversed(range(self.cart_layout.count())):
            item = self.cart_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        total = 0.0
        for pid in self.cart:
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"$ {p['price']}"))
            remove = QtWidgets.QPushButton("Remove")
            remove.clicked.connect(lambda _, pid=pid: self.remove_from_cart(pid))
            row.addWidget(remove)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.cart_layout.addWidget(container)
            total += p['price']
        self.cart_layout.addWidget(QtWidgets.QLabel(f"Total: $ {total}"))
        pay_btn = QtWidgets.QPushButton("Checkout / Pay")
        pay_btn.clicked.connect(self.checkout)
        self.cart_layout.addWidget(pay_btn)
        self.stack.setCurrentWidget(self.cart_page)

    def remove_from_cart(self, pid):
        self.cart = [x for x in self.cart if x != pid]
        self.show_cart()

    def checkout(self):
        if not self.cart:
            QtWidgets.QMessageBox.information(self, "Checkout", "Your cart is empty")
            return
        total = sum(get_product_by_id(pid)['price'] for pid in self.cart)
        modes = ("Cash on Delivery", "Card", "UPI")
        mode, ok = QtWidgets.QInputDialog.getItem(self, "Payment", f"Total: $ {total}\nChoose payment mode:", modes, 0, False)
        if ok:
            QtWidgets.QMessageBox.information(self, "Paid", f"Payment mode: {mode}\nAmount: $ {total}\nThank you for your purchase!")
            self.cart = []
            self.show_cart()

    def show_wishlist(self):
        for i in reversed(range(self.wishlist_layout.count())):
            item = self.wishlist_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for pid in list(self.wishlist):
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"$ {p['price']}"))
            add_cart = QtWidgets.QPushButton("Add to Cart")
            add_cart.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
            row.addWidget(add_cart)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.wishlist_layout.addWidget(container)
        self.stack.setCurrentWidget(self.wishlist_page)


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - JewelMart")
        self.resize(300, 140)
        layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btns = QtWidgets.QHBoxLayout()
        login_btn = QtWidgets.QPushButton("Login")
        reg_btn = QtWidgets.QPushButton("Register")
        btns.addWidget(login_btn)
        btns.addWidget(reg_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        login_btn.clicked.connect(self.handle_login)
        reg_btn.clicked.connect(self.open_register)
        self.user = None

    def handle_login(self):
        users = load_users()
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        if email in users and users[email]["password"] == pwd:
            self.user = users[email]
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login failed", "Invalid email or password")

    def open_register(self):
        dlg = RegistrationDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Registered", "Account created. You can login now.")


class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - JewelMart")
        self.resize(320, 180)
        layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        self.name = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Name:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)
        layout.addLayout(form)
        btn = QtWidgets.QPushButton("Create Account")
        btn.clicked.connect(self.create_account)
        layout.addWidget(btn)
        self.setLayout(layout)

    def create_account(self):
        users = load_users()
        email = self.email.text().strip()
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Email required")
            return
        if email in users:
            QtWidgets.QMessageBox.warning(self, "Error", "User already exists")
            return
        users[email] = {"name": self.name.text().strip(), "password": self.password.text().strip()}
        save_users(users)
        self.accept()


class ProductWidget(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(int)

    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        layout = QtWidgets.QHBoxLayout()
        self.img_label = QtWidgets.QLabel()
        pix = pixmap_for_product(self.product, size=(80, 80))
        self.img_label.setPixmap(pix)
        layout.addWidget(self.img_label)
        v = QtWidgets.QVBoxLayout()
        name_label = QtWidgets.QLabel(f"{product['name']}")
        name_label.setProperty("role", "productName")
        price_label = QtWidgets.QLabel(f"₹ {product['price']:,}")
        price_label.setProperty("role", "productPrice")
        v.addWidget(name_label)
        v.addWidget(price_label)
        layout.addLayout(v)
        self.setLayout(layout)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.product['id'])

    def create_category_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Categories"))
        btn_layout = QtWidgets.QHBoxLayout()
        for c in categories:
            b = QtWidgets.QPushButton(c)
            b.clicked.connect(lambda _, cat=c: self.open_category(cat))
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)
        w.setLayout(layout)
        return w

    def create_products_page(self):
        w = QtWidgets.QWidget()
        self.products_layout = QtWidgets.QVBoxLayout()
        sc = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        container.setLayout(self.products_layout)
        sc.setWidget(container)
        sc.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(sc)
        w.setLayout(layout)
        return w

    def create_product_detail(self):
        w = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout()
        w.setLayout(self.detail_layout)
        return w

    def create_cart_page(self):
        w = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout()
        w.setLayout(self.cart_layout)
        return w

    def create_wishlist_page(self):
        w = QtWidgets.QWidget()
        self.wishlist_layout = QtWidgets.QVBoxLayout()
        w.setLayout(self.wishlist_layout)
        return w

    def create_contact_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Email:", QtWidgets.QLineEdit())
        layout.addRow("Message:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Send"))
        w.setLayout(layout)
        return w

    def create_about_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("About JewelMart"))
        layout.addWidget(QtWidgets.QLabel("JewelMart is a demo desktop application showcasing jewelry catalogs."))
        w.setLayout(layout)
        return w

    def create_feedback_page(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        layout.addRow("Name:", QtWidgets.QLineEdit())
        layout.addRow("Rating (1-5):", QtWidgets.QSpinBox())
        layout.addRow("Comments:", QtWidgets.QTextEdit())
        layout.addRow(QtWidgets.QPushButton("Submit"))
        w.setLayout(layout)
        return w

    def show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.user = dlg.user
            self.statusBar().showMessage(f"Logged in as {self.user.get('name','')}")

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_category(self, cat):
        # populate products layout
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        prods = get_products(cat)
        for p in prods:
            pw = ProductWidget(p)
            pw.clicked.connect(self.open_product)
            self.products_layout.addWidget(pw)
        self.stack.setCurrentWidget(self.products_page)

    def open_product(self, pid):
        prod = get_product_by_id(pid)
        if not prod:
            return
        # clear detail
        for i in reversed(range(self.detail_layout.count())):
            item = self.detail_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        h = QtWidgets.QHBoxLayout()
        pix = pixmap_for_product(prod, size=(240, 240))
        img = QtWidgets.QLabel()
        img.setPixmap(pix)
        h.addWidget(img)
        v = QtWidgets.QVBoxLayout()
        name_lbl = QtWidgets.QLabel(prod['name'])
        name_lbl.setProperty("role", "productName")
        price_lbl = QtWidgets.QLabel(f"Price: ₹ {prod['price']:,}")
        price_lbl.setProperty("role", "productPrice")
        v.addWidget(name_lbl)
        v.addWidget(price_lbl)
        v.addWidget(QtWidgets.QLabel(prod.get('description','')))
        wish_btn = QtWidgets.QPushButton("Add to Wishlist")
        cart_btn = QtWidgets.QPushButton("Add to Cart")
        tryon_btn = QtWidgets.QPushButton("Virtual Try-On")
        wish_btn.clicked.connect(lambda _, pid=pid: self.add_to_wishlist(pid))
        cart_btn.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
        tryon_btn.clicked.connect(lambda _, pid=pid: self.virtual_tryon(pid))
        v.addWidget(wish_btn)
        v.addWidget(cart_btn)
        v.addWidget(tryon_btn)
        h.addLayout(v)
        self.detail_layout.addLayout(h)
        self.stack.setCurrentWidget(self.product_detail_page)

    def add_to_wishlist(self, pid):
        self.wishlist.add(pid)
        QtWidgets.QMessageBox.information(self, "Wishlist", "Added to wishlist")

    def add_to_cart(self, pid):
        self.cart.append(pid)
        QtWidgets.QMessageBox.information(self, "Cart", "Added to cart")

    def virtual_tryon(self, pid):
        prod = get_product_by_id(pid)
        # Try to find a try-on module at JewelMart/tryon/run.py or JewelMart/tryon.py
        base = os.path.dirname(__file__)
        tryon_folder = os.path.join(base, "tryon")
        # Preferred entry points
        candidates = [
            os.path.join(tryon_folder, "run.py"),
            os.path.join(tryon_folder, "__init__.py"),
            os.path.join(base, "tryon.py"),
        ]
        for c in candidates:
            if os.path.exists(c):
                try:
                    spec = importlib.util.spec_from_file_location("jewel_tryon", c)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    # look for common entry names
                    if hasattr(mod, "launch"):
                        mod.launch(prod)
                        return
                    if hasattr(mod, "run_tryon"):
                        mod.run_tryon(prod)
                        return
                    if hasattr(mod, "main"):
                        mod.main(prod)
                        return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Try-On Error", f"Error launching try-on: {e}")
                    return
        # If we get here, no tryon module found
        QtWidgets.QMessageBox.information(
            self,
            "Virtual Try-On",
            "No try-on module found. To enable virtual try-on, place your try-on folder at:\n"
            + os.path.join(base, "tryon")
            + "\nwith an entry file `run.py` exposing one of: launch(product), run_tryon(product) or main(product).",
        )

    def toggle_theme(self):
        # Load current settings (app.py exposes helpers if run via app.py)
        settings = {"theme": "light"}
        try:
            # try to use window-provided loader
            if hasattr(self, "_load_settings"):
                settings = self._load_settings() or settings
            else:
                settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
        except Exception:
            settings = {"theme": "light"}
        new_theme = "light" if settings.get("theme") == "light" else "dark"
        settings["theme"] = new_theme
        # Save
        try:
            if hasattr(self, "_save_settings"):
                self._save_settings(settings)
            else:
                settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)
        except Exception:
            pass
        # Apply immediately to app
        try:
            qss_name = "style.qss" if new_theme == "dark" else "style_light.qss"
            qss_path = os.path.join(os.path.dirname(__file__), qss_name)
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    QtWidgets.QApplication.instance().setStyleSheet(f.read())
        except Exception:
            pass

    def show_cart(self):
        # populate cart page
        for i in reversed(range(self.cart_layout.count())):
            item = self.cart_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        total = 0.0
        for pid in self.cart:
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"$ {p['price']}"))
            remove = QtWidgets.QPushButton("Remove")
            remove.clicked.connect(lambda _, pid=pid: self.remove_from_cart(pid))
            row.addWidget(remove)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.cart_layout.addWidget(container)
            total += p['price']
        self.cart_layout.addWidget(QtWidgets.QLabel(f"Total: $ {total}"))
        pay_btn = QtWidgets.QPushButton("Checkout / Pay")
        pay_btn.clicked.connect(self.checkout)
        self.cart_layout.addWidget(pay_btn)
        self.stack.setCurrentWidget(self.cart_page)

    def remove_from_cart(self, pid):
        self.cart = [x for x in self.cart if x != pid]
        self.show_cart()

    def checkout(self):
        if not self.cart:
            QtWidgets.QMessageBox.information(self, "Checkout", "Your cart is empty")
            return
        total = sum(get_product_by_id(pid)['price'] for pid in self.cart)
        modes = ("Cash on Delivery", "Card", "UPI")
        mode, ok = QtWidgets.QInputDialog.getItem(self, "Payment", f"Total: $ {total}\nChoose payment mode:", modes, 0, False)
        if ok:
            QtWidgets.QMessageBox.information(self, "Paid", f"Payment mode: {mode}\nAmount: $ {total}\nThank you for your purchase!")
            self.cart = []
            self.show_cart()

    def show_wishlist(self):
        for i in reversed(range(self.wishlist_layout.count())):
            item = self.wishlist_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()
        for pid in list(self.wishlist):
            p = get_product_by_id(pid)
            if not p:
                continue
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(p['name']))
            row.addWidget(QtWidgets.QLabel(f"$ {p['price']}"))
            add_cart = QtWidgets.QPushButton("Add to Cart")
            add_cart.clicked.connect(lambda _, pid=pid: self.add_to_cart(pid))
            row.addWidget(add_cart)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.wishlist_layout.addWidget(container)
        self.stack.setCurrentWidget(self.wishlist_page)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
