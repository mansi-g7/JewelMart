"""JewelMart UI - PyQt5 application with video home page and virtual try-on."""

import os
import json
import importlib.util
import cv2
import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtMultimedia, QtMultimediaWidgets
try:
    from PyQt5 import QtWebEngineWidgets
    WEB_ENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    WEB_ENGINE_AVAILABLE = False


class VideoThread(QtCore.QThread):
    """Threaded OpenCV video reader that emits QImage frames."""
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

            # Determine FPS and delay
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            if fps <= 0 or fps > 120:
                fps = 25.0
            delay_ms = int(1000.0 / fps)

            emitted_first = False
            while self._running:
                ret, frame = cap.read()
                if not ret:
                    # try to loop
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
                    if not emitted_first:
                        log_debug(f"[VIDEO_THREAD] emitted first frame {w}x{h}")
                        emitted_first = True
                except Exception:
                    pass

                self.msleep(max(1, delay_ms))

            cap.release()
        except Exception:
            pass

    def stop(self):
        self._running = False
        try:
            self.wait(1000)
        except Exception:
            pass


def log_debug(msg: str):
    """Write simple debug messages to `home_debug.log` and stdout."""
    try:
        logpath = os.path.join(os.path.dirname(__file__), 'home_debug.log')
        with open(logpath, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass
    try:
        print(msg)
    except Exception:
        pass


# Write a module load marker so we know ui.py was imported/executed
try:
    log_debug("[UI] ui.py module loaded")
except Exception:
    pass



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
        # Start/stop playback when stack page changes
        self.stack.currentChanged.connect(lambda idx: self.on_page_changed(idx))
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
        log_debug(f"[HOME] Video: {HOME_VIDEO_URL}")
        # Create video widget + poster stack
        video_widget = QtMultimediaWidgets.QVideoWidget()
        video_widget.setStyleSheet("background-color: black;")

        # Poster (fallback) - load first image in assets if possible
        poster_label = QtWidgets.QLabel()
        poster_label.setAlignment(QtCore.Qt.AlignCenter)
        poster_label.setStyleSheet("background-color: black;")
        poster_pixmap = None
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        if os.path.exists(assets_dir):
            for f in os.listdir(assets_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        poster_pixmap = QtGui.QPixmap(os.path.join(assets_dir, f))
                        break
                    except Exception:
                        poster_pixmap = None

        if poster_pixmap is None:
            # generate a simple poster
            poster_pixmap = QtGui.QPixmap(1024, 576)
            poster_pixmap.fill(QtGui.QColor(15, 15, 25))
            p = QtGui.QPainter(poster_pixmap)
            p.setPen(QtGui.QColor(220, 180, 200))
            font = QtGui.QFont("Arial", 36, QtGui.QFont.Bold)
            p.setFont(font)
            p.drawText(poster_pixmap.rect(), QtCore.Qt.AlignCenter, "JewelMart")
            p.end()

        poster_label.setPixmap(poster_pixmap.scaled(960, 540, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        # Create a stacked widget to switch between poster, label (OpenCV) and native video
        display_stack = QtWidgets.QStackedWidget()
        display_stack.addWidget(poster_label)

        # Video label (for OpenCV frames)
        video_label = QtWidgets.QLabel()
        video_label.setAlignment(QtCore.Qt.AlignCenter)
        video_label.setStyleSheet("background-color: black;")
        # Ensure label has a reasonable minimum size so initial frames are visible
        video_label.setMinimumSize(640, 360)
        display_stack.addWidget(video_label)

        display_stack.addWidget(video_widget)
        layout.addWidget(display_stack, 1)

        # Button row - open externally
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        open_btn = QtWidgets.QPushButton("Open video in external player")
        open_btn.setToolTip("Open the home video in your system's default player")
        btn_row.addWidget(open_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Save references for later
        self.display_stack = display_stack
        self.video_widget = video_widget
        self.video_label = video_label
        self.poster_label = poster_label
        self.open_video_button = open_btn

        # Connect external open button
        open_btn.clicked.connect(self.open_video_external)

        # Create media player (keep as fallback)
        self.media_player = QtMultimedia.QMediaPlayer()
        self.media_player.setVideoOutput(video_widget)

        # We'll start OpenCV playback only when Home is shown to ensure widgets are laid out
        self.video_thread = None
        self._opencv_playback_available = False
        try:
            if HOME_VIDEO_URL and os.path.exists(HOME_VIDEO_URL):
                tmp_cap = cv2.VideoCapture(HOME_VIDEO_URL)
                if tmp_cap.isOpened():
                    self._opencv_playback_available = True
                tmp_cap.release()
        except Exception:
            self._opencv_playback_available = False

        # Leave starting playback to show_home() so label sizes/layout exist

        log_debug(f"[HOME] ========== READY ==========")
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
        log_debug(f"[HOME] Media status: {status_map.get(status, str(status))}")
        
        # If media is invalid or missing, show poster and keep an external-open option
        if status in (QtMultimedia.QMediaPlayer.NoMedia, QtMultimedia.QMediaPlayer.InvalidMedia):
            try:
                if hasattr(self, 'display_stack') and hasattr(self, 'poster_label'):
                    self.display_stack.setCurrentWidget(self.poster_label)
                    log_debug(f"[HOME] Showing poster fallback (media unavailable)")
            except Exception:
                pass

        # When loaded/buffered/playing, switch to video widget
        if status in (QtMultimedia.QMediaPlayer.LoadedMedia, QtMultimedia.QMediaPlayer.BufferedMedia, QtMultimedia.QMediaPlayer.BufferingMedia):
            try:
                if hasattr(self, 'display_stack') and hasattr(self, 'video_widget'):
                    self.display_stack.setCurrentWidget(self.video_widget)
                log_debug(f"[HOME] Switched to video widget")
            except Exception:
                pass

        # Loop: restart when finished
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            log_debug(f"[HOME] End of video, restarting...")
            try:
                self.media_player.setPosition(0)
                self.media_player.play()
            except Exception:
                pass
    
    def on_player_state_changed(self, state):
        """Handle player state changes."""
        state_map = {
            QtMultimedia.QMediaPlayer.StoppedState: "Stopped",
            QtMultimedia.QMediaPlayer.PlayingState: "Playing",
            QtMultimedia.QMediaPlayer.PausedState: "Paused",
        }
        log_debug(f"[HOME] Player state: {state_map.get(state, str(state))}")
    
    def on_position_changed(self, position):
        """Handle position changes."""
        pass  # Suppress verbose logging
    
    def on_duration_changed(self, duration):
        """Handle duration changes."""
        log_debug(f"[HOME] Video duration: {duration}ms")

    def open_video_external(self):
        """Open the HOME_VIDEO_URL in the system's default external player."""
        try:
            if not HOME_VIDEO_URL or not os.path.exists(HOME_VIDEO_URL):
                QtWidgets.QMessageBox.information(self, "Open video", "Video file not found.")
                return

            log_debug(f"[HOME] Opening video externally: {HOME_VIDEO_URL}")
            if os.name == 'nt':
                os.startfile(HOME_VIDEO_URL)
            else:
                import subprocess, platform
                if platform.system() == 'Darwin':
                    subprocess.Popen(['open', HOME_VIDEO_URL])
                else:
                    subprocess.Popen(['xdg-open', HOME_VIDEO_URL])
        except Exception as e:
            log_debug(f"[HOME] open_video_external ERROR: {e}")
            QtWidgets.QMessageBox.warning(self, "Open video", f"Could not open video externally: {e}")

    def update_frame(self, qimg: QtGui.QImage):
        """Slot to receive QImage frames from VideoThread and display them."""
        try:
            if qimg is None or qimg.isNull():
                return
            pix = QtGui.QPixmap.fromImage(qimg)
            if pix.isNull():
                return
            # scale to label while keeping aspect
            lbl = getattr(self, 'video_label', None)
            if lbl is not None:
                # If label hasn't been laid out yet its size may be 0; use display_stack size or a default
                target_size = lbl.size()
                if target_size.width() < 2 or target_size.height() < 2:
                    try:
                        target_size = getattr(self, 'display_stack').size()
                    except Exception:
                        target_size = QtCore.QSize(960, 540)

                scaled = pix.scaled(target_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                # draw a small frame counter overlay for debugging
                try:
                    count = getattr(self, '_frame_count', 0) + 1
                    self._frame_count = count
                    overlay = QtGui.QPixmap(scaled)
                    painter = QtGui.QPainter(overlay)
                    painter.setRenderHint(QtGui.QPainter.Antialiasing)
                    rect = QtCore.QRect(8, overlay.height() - 30, 120, 24)
                    painter.fillRect(rect, QtGui.QColor(0, 0, 0, 140))
                    painter.setPen(QtGui.QColor(255, 255, 255))
                    painter.setFont(QtGui.QFont('Arial', 10))
                    painter.drawText(rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, f"Frames: {count}")
                    painter.end()
                    lbl.setPixmap(overlay)
                    # log first frame and periodic progress so we can debug
                    if count == 1 or (count % 50) == 0:
                        log_debug(f"[HOME] update_frame: displayed frame #{count}")
                except Exception:
                    lbl.setPixmap(scaled)
                lbl.repaint()
                try:
                    # switch to the video label so it's visible
                    self.display_stack.setCurrentWidget(self.video_label)
                except Exception:
                    pass
        except Exception:
            pass

    def closeEvent(self, event):
        # stop video thread if running
        try:
            if hasattr(self, 'video_thread') and self.video_thread is not None:
                self.video_thread.stop()
        except Exception:
            pass
        try:
            super().closeEvent(event)
        except Exception:
            event.accept()

    
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
        # starting playback is handled by on_page_changed when the stack index changes

    def start_home_video(self):
        """Start video playback for Home: prefer OpenCV threaded playback, fall back to QMediaPlayer."""
        # if already running, ignore
        if getattr(self, 'video_thread', None) is not None:
            return

        if getattr(self, '_opencv_playback_available', False):
            try:
                log_debug(f"[HOME] Starting OpenCV threaded playback on show")
                self.video_thread = VideoThread(HOME_VIDEO_URL)
                self.video_thread.frame_ready.connect(self.update_frame)
                self.video_thread.start()
                # switch to video_label
                try:
                    self.display_stack.setCurrentWidget(self.video_label)
                except Exception:
                    pass
                return
            except Exception as e:
                log_debug(f"[HOME] OpenCV start error: {e}")

        # Fallback: use QMediaPlayer
        try:
            log_debug(f"[HOME] Falling back to QMediaPlayer on show")
            media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(HOME_VIDEO_URL))
            self.media_player.setMedia(media)
            self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
            self.media_player.stateChanged.connect(self.on_player_state_changed)
            self.media_player.positionChanged.connect(self.on_position_changed)
            self.media_player.durationChanged.connect(self.on_duration_changed)
            try:
                self.media_player.setVolume(0)
            except Exception:
                pass
            self.media_player.play()
        except Exception as e:
            log_debug(f"[HOME] QMediaPlayer fallback error: {e}")

    def stop_home_video(self):
        """Stop any running home video playback (thread or media player)."""
        try:
            if getattr(self, 'video_thread', None) is not None:
                log_debug(f"[HOME] Stopping OpenCV thread")
                try:
                    self.video_thread.stop()
                except Exception:
                    pass
                self.video_thread = None
        except Exception:
            pass
        try:
            if getattr(self, 'media_player', None) is not None:
                try:
                    self.media_player.stop()
                except Exception:
                    pass
        except Exception:
            pass

    def on_page_changed(self, idx: int):
        """Called when the stacked widget page changes. Start/stop home playback."""
        try:
            # Home page index is 1
            if idx == 1:
                log_debug(f"[HOME] on_page_changed: index=1 -> start_home_video")
                self.start_home_video()
            else:
                log_debug(f"[HOME] on_page_changed: index={idx} -> stop_home_video")
                self.stop_home_video()
        except Exception as e:
            log_debug(f"[HOME] on_page_changed error: {e}")
    
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

        def navigate_to(idx):
            # Stop home playback if leaving home
            try:
                if idx != 1 and hasattr(self, 'video_thread') and self.video_thread is not None:
                    self.stop_home_video()
            except Exception:
                pass
            # show the requested page
            if idx == -1:
                self.logout()
            else:
                self.stack.setCurrentIndex(idx)

        for name, idx in pages:
            btn = QtWidgets.QPushButton(name)
            if idx == -1:
                btn.clicked.connect(self.logout)
            else:
                btn.clicked.connect(lambda checked, i=idx: navigate_to(i))
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
