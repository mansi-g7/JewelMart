"""Clean UI used by app.py to avoid prior corrupted ui.py.

Provides MainWindow with WebEngine-first HTML5 video on home page and a
QtMultimedia fallback displaying a poster/message when playback fails.
"""

import os
import json
import importlib.util
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets
import cv2

try:
    from PyQt5 import QtWebEngineWidgets
    WEB_ENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    WEB_ENGINE_AVAILABLE = False

from data import categories, get_products, get_product_by_id, HOME_VIDEO_URL


class VideoThread(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self._running = True

    def run(self):
        try:
            cap = cv2.VideoCapture(self.path)
            if not cap.isOpened():
                return
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            if fps <= 0 or fps > 120:
                fps = 25.0
            delay = int(1000.0 / fps)
            while self._running:
                ret, frame = cap.read()
                if not ret:
                    try:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    except Exception:
                        break
                try:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb.shape
                    bytes_per_line = ch * w
                    qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                    self.frame_ready.emit(qimg.copy())
                except Exception:
                    pass
                self.msleep(max(1, delay))
            cap.release()
        except Exception:
            pass

    def stop(self):
        self._running = False
        try:
            self.wait(1000)
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
        # permissive: allow any non-empty email/password for demo
        email = self.email.text().strip()
        if email:
            self.user = {"name": email}
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login failed", "Enter an email")

    def open_register(self):
        dlg = RegistrationDialog(self)
        dlg.exec_()


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
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


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
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = self.create_home()
        self.stack.addWidget(self.home_page)

    def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        # Try OpenCV-based playback first (works reliably where codecs are available to OpenCV)
        try:
            if HOME_VIDEO_URL and os.path.exists(HOME_VIDEO_URL):
                tmp = cv2.VideoCapture(HOME_VIDEO_URL)
                if tmp.isOpened():
                    tmp.release()
                    video_label = QtWidgets.QLabel()
                    video_label.setAlignment(QtCore.Qt.AlignCenter)
                    video_label.setMinimumSize(640, 360)
                    layout.addWidget(video_label, 1)

                    thread = VideoThread(HOME_VIDEO_URL)
                    def _on_frame(qimg, lbl=video_label):
                        try:
                            pix = QtGui.QPixmap.fromImage(qimg)
                            if not pix.isNull():
                                sz = lbl.size()
                                if sz.width() < 2 or sz.height() < 2:
                                    sz = QtCore.QSize(960, 540)
                                scaled = pix.scaled(sz, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                                # overlay a small frame counter for diagnostics
                                try:
                                    count = getattr(self, '_home_frame_count', 0) + 1
                                    self._home_frame_count = count
                                    overlay = QtGui.QPixmap(scaled)
                                    painter = QtGui.QPainter(overlay)
                                    rect = QtCore.QRect(8, overlay.height() - 30, 140, 24)
                                    painter.fillRect(rect, QtGui.QColor(0, 0, 0, 140))
                                    painter.setPen(QtGui.QColor(255, 255, 255))
                                    painter.setFont(QtGui.QFont('Arial', 10))
                                    painter.drawText(rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, f"Frames: {count}")
                                    painter.end()
                                    lbl.setPixmap(overlay)
                                except Exception:
                                    lbl.setPixmap(scaled)
                        except Exception:
                            pass

                    thread.frame_ready.connect(_on_frame)
                    thread.start()
                    # keep reference so thread is not GC'd
                    self._home_video_thread = thread
                    return w
        except Exception:
            pass

        if HOME_VIDEO_URL:
            if WEB_ENGINE_AVAILABLE and QtWebEngineWidgets is not None:
                try:
                    view = QtWebEngineWidgets.QWebEngineView()
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
            player = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
            playlist = QtMultimedia.QMediaPlaylist()
            url_obj = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL) if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl(HOME_VIDEO_URL)
            playlist.addMedia(QtMultimedia.QMediaContent(url_obj))
            playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)
            player.setPlaylist(playlist)
            player.setVideoOutput(video_widget)
            try:
                player.setMuted(True)
            except Exception:
                pass
            player.play()
            layout.addWidget(video_widget, 1)
        else:
            layout.addWidget(QtWidgets.QLabel("Welcome to JewelMart"))

        return w


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
import json
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets

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
        self.resize(320, 160)
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
        self.resize(360, 220)
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

        # create header / sidebar / content / footer layout
        central = QtWidgets.QWidget()
        central_layout = QtWidgets.QVBoxLayout(central)

        # header
        header = self.create_header()
        central_layout.addWidget(header)

        # main content area: sidebar + stacked pages
        content_h = QtWidgets.QHBoxLayout()
        self.sidebar = self.create_sidebar()
        content_h.addWidget(self.sidebar)
        content_h.addWidget(self.stack, 1)
        central_layout.addLayout(content_h, 1)

        # footer
        footer = self.create_footer()
        central_layout.addWidget(footer)

        self.setCentralWidget(central)

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

    def create_header(self):
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        title = QtWidgets.QLabel("JewelMart")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        search = QtWidgets.QLineEdit()
        search.setPlaceholderText("Search products...")
        search.setMaximumWidth(300)
        login_btn = QtWidgets.QPushButton("Login")
        login_btn.clicked.connect(self.show_login)
        h.addWidget(title)
        h.addStretch(1)
        h.addWidget(search)
        h.addWidget(login_btn)
        return w

    def create_footer(self):
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        h.addStretch(1)
        h.addWidget(QtWidgets.QLabel("© JewelMart - Demo"))
        h.addStretch(1)
        return w

    def create_sidebar(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        lbl = QtWidgets.QLabel("Categories")
        lbl.setStyleSheet("font-weight: bold;")
        v.addWidget(lbl)
        for c in categories:
            b = QtWidgets.QPushButton(c)
            b.clicked.connect(lambda _, cat=c: self.open_category(cat))
            v.addWidget(b)
        v.addStretch(1)
        login_btn = QtWidgets.QPushButton("Login")
        login_btn.clicked.connect(self.show_login)
        v.addWidget(login_btn)
        contact_btn = QtWidgets.QPushButton("Contact Us")
        contact_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.contact_page))
        v.addWidget(contact_btn)
        about_btn = QtWidgets.QPushButton("About Us")
        about_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.about_page))
        v.addWidget(about_btn)
        return w

    def create_home(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        # show only the video when configured
        if HOME_VIDEO_URL:
            # Try WebEngine (HTML5) first
            if WEB_ENGINE_AVAILABLE and QtWebEngineWidgets is not None:
                try:
                    web = QtWebEngineWidgets.QWebEngineView()
                    src = QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL).toString() if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl(HOME_VIDEO_URL).toString()
                    html = f'''<!doctype html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;background:black;">
  <video autoplay loop muted playsinline style="width:100%;height:100%;object-fit:cover;">
    <source src="{src}" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</body></html>'''
                    base = QtCore.QUrl.fromLocalFile(os.path.dirname(HOME_VIDEO_URL)) if os.path.exists(HOME_VIDEO_URL) else QtCore.QUrl("./")
                    web.setHtml(html, base)
                    layout.addWidget(web, 1)
                    return w
                except Exception:
                    pass

            # Fall back to QtMultimedia player
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

