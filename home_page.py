"""
Home Page Module for JewelMart
Features:
- Overview section with app description
- Image carousel/slideshow with beautiful product showcase images
- Interactive navigation
"""

from PyQt5 import QtWidgets, QtGui, QtCore
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class ImageCarousel(QtWidgets.QWidget):
    """Image carousel/slideshow widget with navigation"""
    
    def __init__(self, images=None):
        super().__init__()
        self.images = images or []
        self.current_index = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_image)
        
        self.init_ui()
        
        # Auto-play carousel every 5 seconds
        if self.images:
            self.timer.start(5000)
    
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Image display
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setFixedHeight(400)
        self.image_label.setStyleSheet("background-color: #F5F5F5; border-radius: 8px;")
        layout.addWidget(self.image_label)
        
        # Controls
        controls = QtWidgets.QHBoxLayout()
        
        prev_btn = QtWidgets.QPushButton("◀ Previous")
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #C8937E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B5845E;
            }
        """)
        prev_btn.clicked.connect(self.prev_image)
        controls.addWidget(prev_btn)
        
        self.slide_counter = QtWidgets.QLabel()
        self.slide_counter.setStyleSheet("font-weight: bold; color: #666666;")
        self.slide_counter.setAlignment(QtCore.Qt.AlignCenter)
        controls.addWidget(self.slide_counter)
        
        next_btn = QtWidgets.QPushButton("Next ▶")
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #C8937E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B5845E;
            }
        """)
        next_btn.clicked.connect(self.next_image)
        controls.addWidget(next_btn)
        
        layout.addLayout(controls)
        
        # Dot indicators
        dots_layout = QtWidgets.QHBoxLayout()
        dots_layout.addStretch()
        self.dots = []
        for i in range(len(self.images)):
            dot = QtWidgets.QPushButton()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet("""
                QPushButton {
                    background-color: #CCCCCC;
                    border: none;
                    border-radius: 6px;
                }
            """)
            dot.clicked.connect(lambda checked, idx=i: self.go_to_image(idx))
            dots_layout.addWidget(dot)
            self.dots.append(dot)
        dots_layout.addStretch()
        layout.addLayout(dots_layout)
        
        self.display_image()
    
    def display_image(self):
        """Display the current image"""
        if not self.images:
            self.image_label.setText("No images available")
            return
        
        img_path = self.images[self.current_index]
        if os.path.exists(img_path):
            pixmap = QtGui.QPixmap(img_path).scaled(800, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText(f"Image not found: {os.path.basename(img_path)}")
        
        # Update counter
        self.slide_counter.setText(f"{self.current_index + 1} / {len(self.images)}")
        
        # Update dots
        for i, dot in enumerate(self.dots):
            if i == self.current_index:
                dot.setStyleSheet("""
                    QPushButton {
                        background-color: #C8937E;
                        border: none;
                        border-radius: 6px;
                    }
                """)
            else:
                dot.setStyleSheet("""
                    QPushButton {
                        background-color: #CCCCCC;
                        border: none;
                        border-radius: 6px;
                    }
                """)
    
    def next_image(self):
        """Go to next image"""
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self.display_image()
    
    def prev_image(self):
        """Go to previous image"""
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.display_image()
    
    def go_to_image(self, index):
        """Go to a specific image"""
        if 0 <= index < len(self.images):
            self.current_index = index
            self.display_image()
    
    def stop_auto_play(self):
        """Stop the automatic slideshow"""
        self.timer.stop()
    
    def start_auto_play(self):
        """Start the automatic slideshow"""
        if self.images:
            self.timer.start(5000)


class HomePage(QtWidgets.QWidget):
    """Home page with overview and image carousel"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the home page UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Welcome banner
        welcome = QtWidgets.QLabel("Welcome to JewelMart")
        welcome.setStyleSheet("""
            color: #C8937E;
            font-size: 32px;
            font-weight: bold;
        """)
        welcome.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(welcome)
        
        # Tagline
        tagline = QtWidgets.QLabel("Discover Luxury Jewelry | Premium Quality | Exquisite Designs")
        tagline.setStyleSheet("""
            color: #666666;
            font-size: 14px;
            font-style: italic;
        """)
        tagline.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(tagline)
        
        main_layout.addSpacing(20)
        
        # Image carousel
        images = self.get_carousel_images()
        carousel = ImageCarousel(images)
        main_layout.addWidget(carousel)
        
        main_layout.addSpacing(20)
        
        # Overview section
        overview_title = QtWidgets.QLabel("About Our Collection")
        overview_title.setStyleSheet("""
            color: #333333;
            font-size: 20px;
            font-weight: bold;
        """)
        main_layout.addWidget(overview_title)
        
        # Overview text
        overview_text = QtWidgets.QLabel(
            "JewelMart is your premier destination for exquisite jewelry and luxury accessories. "
            "We offer a carefully curated selection of:\n\n"
            "💎 <b>Premium Jewelry</b> - Handcrafted pieces from master artisans\n"
            "✨ <b>Exclusive Designs</b> - Unique styles you won't find elsewhere\n"
            "🎯 <b>Quality Assured</b> - Certified materials and expert craftsmanship\n"
            "🚚 <b>Fast Delivery</b> - Secure packaging and quick shipping\n"
            "💳 <b>Easy Checkout</b> - Simple and secure payment options\n\n"
            "Browse our collection by category, add items to your cart, and experience "
            "the JewelMart difference. Every piece tells a story of elegance and sophistication."
        )
        overview_text.setWordWrap(True)
        overview_text.setStyleSheet("""
            color: #555555;
            font-size: 13px;
            line-height: 1.6;
            padding: 15px;
            background-color: #F9F9F9;
            border-radius: 6px;
            border-left: 4px solid #C8937E;
        """)
        main_layout.addWidget(overview_text)
        
        main_layout.addSpacing(20)
        
        # Quick stats
        stats_layout = QtWidgets.QHBoxLayout()
        
        for stat_title, stat_value in [("Collections", "50+"), ("Products", "500+"), ("Customers", "10K+")]:
            stat_widget = QtWidgets.QWidget()
            stat_widget.setStyleSheet("""
                background-color: #FFFFFF;
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                padding: 20px;
            """)
            stat_layout = QtWidgets.QVBoxLayout(stat_widget)
            stat_layout.setAlignment(QtCore.Qt.AlignCenter)
            
            value_label = QtWidgets.QLabel(stat_value)
            value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #C8937E;")
            value_label.setAlignment(QtCore.Qt.AlignCenter)
            stat_layout.addWidget(value_label)
            
            title_label = QtWidgets.QLabel(stat_title)
            title_label.setStyleSheet("font-size: 12px; color: #666666;")
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            stat_layout.addWidget(title_label)
            
            stats_layout.addWidget(stat_widget)
        
        main_layout.addLayout(stats_layout)
        
        # Call-to-action
        cta_label = QtWidgets.QLabel("Ready to explore? Browse our categories using the tabs below!")
        cta_label.setStyleSheet("""
            color: #C8937E;
            font-size: 13px;
            font-weight: bold;
        """)
        cta_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(cta_label)
        
        main_layout.addStretch()
    
    def get_carousel_images(self):
        """Get list of product images for the carousel"""
        if not os.path.exists(ASSETS_DIR):
            return []
        
        # Try to get the first few product images from assets folder
        image_extensions = ("*.jpg", "*.png", "*.jpeg")
        images = []
        
        for ext in image_extensions:
            images.extend(glob.glob(os.path.join(ASSETS_DIR, ext)))
            if len(images) >= 5:
                break
        
        return sorted(images)[:5] if images else []
