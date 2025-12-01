"""
Login & Registration System - Light Golden, Black & White Theme
Pure Python - NO DATABASE (In-Memory Storage)
"""

from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import hashlib
import re

# In-memory storage for users
USERS_DATA = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None


def validate_mobile(mobile: str) -> bool:
    return re.match(r'^\d{10}$', mobile) is not None


def validate_name(name: str) -> bool:
    return re.match(r'^[a-zA-Z\s]+$', name) is not None


def validate_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Must contain lowercase letter"
    if not re.search(r'\d', password):
        return False, "Must contain a number"
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Must contain special character"
    return True, "Valid"


# Global stylesheet (Light Golden Theme)
GOLD_STYLE = """
QMainWindow, QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #FFFFFF, stop:0.5 #FFF8DC, stop:1 #FFD700);
    font-family: 'Segoe UI', Arial;
}

QLabel {
    color: #000000;
    font-size: 14px;
}

QLabel#title {
    color: #000000;
    font-size: 32px;
    font-weight: bold;
}

QLabel#subtitle {
    color: #333333;
    font-size: 14px;
}

QLineEdit, QTextEdit, QComboBox {
    padding: 10px 12px;
    # border: none;
    # border-bottom: 2px solid #FFD700;
    background-color: transparent;
    font-size: 14px;
    min-height: 24px;
    color: #000000;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-bottom: 2px solid #FFA500;
    background-color: transparent;
}

QPushButton#primary {
    padding: 12px;
    # border: none;
    # border-radius: 8px;
    font-size: 15px;
    font-weight: bold;
    color: #000000;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFD700, stop:1 #FFA500);
    min-height: 26px;
}

QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFA500, stop:1 #FF8C00);
}

QPushButton#secondary {
    background-color: transparent;
    color: #B8860B;
    text-decoration: underline;
    # border: none;
    font-size: 13px;
}

QPushButton#secondary:hover {
    color: #FF8C00;
}

QLabel#error {
    color: #FF1493;
    font-size: 12px;
    min-height: 18px;
    background-color: transparent;
    padding: 2px 0px;
}
"""


# ------------------- LOGIN WINDOW -------------------

class LoginWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Light Golden Theme")
        self.setFixedSize(500, 550)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)

        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                # border-radius: 20px;
                # border: 2px solid #FFD700;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        title = QtWidgets.QLabel("Welcome Back")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel("Login to access your account")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(20)

        # Email
        email_container = QtWidgets.QVBoxLayout()
        email_container.setSpacing(6)

        email_label = QtWidgets.QLabel("Email Address *")
        email_label.setStyleSheet("font-weight: bold; color: #000000; font-size: 14px;")
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        self.email_input.setFixedHeight(40)

        email_container.addWidget(email_label)
        email_container.addWidget(self.email_input)
        card_layout.addLayout(email_container)

        # Password
        password_container = QtWidgets.QVBoxLayout()
        password_container.setSpacing(6)

        password_label = QtWidgets.QLabel("Password *")
        password_label.setStyleSheet("font-weight: bold; color: #000000; font-size: 14px;")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setFixedHeight(40)

        password_container.addWidget(password_label)
        password_container.addWidget(self.password_input)
        card_layout.addLayout(password_container)

        # Error label
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        card_layout.addWidget(self.error_label)

        # Forgot password
        forgot_btn = QtWidgets.QPushButton("Forgot Password?")
        forgot_btn.setObjectName("secondary")
        forgot_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        forgot_btn.clicked.connect(self.forgot_password)
        card_layout.addWidget(forgot_btn, alignment=QtCore.Qt.AlignRight)

        # Login button
        login_btn = QtWidgets.QPushButton("Login")
        login_btn.setObjectName("primary")
        login_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        login_btn.clicked.connect(self.login)
        card_layout.addWidget(login_btn)

        # Register link
        register_link = QtWidgets.QPushButton("Don't have an account? Register Now")
        register_link.setObjectName("secondary")
        register_link.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        register_link.clicked.connect(self.show_register)
        card_layout.addWidget(register_link, alignment=QtCore.Qt.AlignCenter)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def login(self):
        self.error_label.setText("")
        email = self.email_input.text().strip().lower()
        password = self.password_input.text()

        if not email or not password:
            self.error_label.setText("Please enter both email and password")
            return

        if email not in USERS_DATA:
            self.error_label.setText("Invalid email or password")
            return

        hashed_pwd = hash_password(password)
        if USERS_DATA[email]['password'] != hashed_pwd:
            self.error_label.setText("Invalid email or password")
            return

        QtWidgets.QMessageBox.information(
            self,
            "Success",
            f"Welcome back, {USERS_DATA[email]['full_name']}!"
        )
        # No dashboard, just success

    def forgot_password(self):
        email, ok = QtWidgets.QInputDialog.getText(
            self,
            'Forgot Password',
            'Enter your registered email:'
        )
        if ok and email:
            email = email.strip().lower()
            if not validate_email(email):
                QtWidgets.QMessageBox.warning(self, "Error", "Please enter a valid email")
                return

            if email not in USERS_DATA:
                QtWidgets.QMessageBox.warning(self, "Error", "Email not found")
                return

            self.show_password_reset(email)

    def show_password_reset(self, email):
        dialog = PasswordResetDialog(email, self)
        dialog.exec_()

    def show_register(self):
        main_window = self.window()
        if hasattr(main_window, 'show_register'):
            main_window.show_register()


# ------------------- PASSWORD RESET DIALOG -------------------

class PasswordResetDialog(QtWidgets.QDialog):
    def __init__(self, email, parent=None):
        super().__init__(parent)
        self.email = email
        self.setWindowTitle("Reset Password")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        title = QtWidgets.QLabel("Reset Your Password")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        info = QtWidgets.QLabel(f"Email: {self.email}")
        info.setStyleSheet("color: #666;")
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info)

        layout.addSpacing(10)

        layout.addWidget(QtWidgets.QLabel("New Password:"))
        self.new_password = QtWidgets.QLineEdit()
        self.new_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_password.setPlaceholderText("Enter new password")
        layout.addWidget(self.new_password)

        layout.addWidget(QtWidgets.QLabel("Confirm Password:"))
        self.confirm_password = QtWidgets.QLineEdit()
        self.confirm_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Re-enter new password")
        layout.addWidget(self.confirm_password)

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.error_label)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        reset_btn = QtWidgets.QPushButton("Reset Password")
        reset_btn.setObjectName("primary")
        reset_btn.clicked.connect(self.reset_password)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)

    def reset_password(self):
        self.error_label.setText("")
        new_pwd = self.new_password.text()
        confirm_pwd = self.confirm_password.text()

        if not new_pwd or not confirm_pwd:
            self.error_label.setText("Please fill all fields")
            return

        if new_pwd != confirm_pwd:
            self.error_label.setText("Passwords do not match")
            return

        valid, msg = validate_password(new_pwd)
        if not valid:
            self.error_label.setText(msg)
            return

        USERS_DATA[self.email]['password'] = hash_password(new_pwd)
        QtWidgets.QMessageBox.information(self, "Success", "Password reset successfully!")
        self.accept()


# ------------------- REGISTRATION WINDOW -------------------

class RegistrationWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - Light Golden Theme")
        self.setup_ui()

    def setup_ui(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)

        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                # border-radius: 20px;
                # border: 2px solid #FFD700;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        title = QtWidgets.QLabel("Create Account")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel("Join us today! Fill in your details below")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(15)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        label_style = "font-weight: bold; color: #000000; font-size: 14px;"

        # Full Name
        name_label = QtWidgets.QLabel("Full Name *")
        name_label.setStyleSheet(label_style)
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        form_layout.addRow(name_label, self.name_input)
        self.name_error = QtWidgets.QLabel("")
        self.name_error.setObjectName("error")
        form_layout.addRow("", self.name_error)

        # Gender
        gender_label = QtWidgets.QLabel("Gender *")
        gender_label.setStyleSheet(label_style)
        self.gender_input = QtWidgets.QComboBox()
        self.gender_input.addItems(["Select Gender", "Male", "Female", "Other"])
        form_layout.addRow(gender_label, self.gender_input)
        self.gender_error = QtWidgets.QLabel("")
        self.gender_error.setObjectName("error")
        form_layout.addRow("", self.gender_error)

        # Email
        email_label = QtWidgets.QLabel("Email Address *")
        email_label.setStyleSheet(label_style)
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        form_layout.addRow(email_label, self.email_input)
        self.email_error = QtWidgets.QLabel("")
        self.email_error.setObjectName("error")
        form_layout.addRow("", self.email_error)

        # Mobile
        mobile_label = QtWidgets.QLabel("Mobile Number *")
        mobile_label.setStyleSheet(label_style)
        self.mobile_input = QtWidgets.QLineEdit()
        self.mobile_input.setPlaceholderText("10-digit mobile number")
        self.mobile_input.setMaxLength(10)
        form_layout.addRow(mobile_label, self.mobile_input)
        self.mobile_error = QtWidgets.QLabel("")
        self.mobile_error.setObjectName("error")
        form_layout.addRow("", self.mobile_error)

        # Address
        address_label = QtWidgets.QLabel("Address *")
        address_label.setStyleSheet(label_style)
        self.address_input = QtWidgets.QTextEdit()
        self.address_input.setPlaceholderText("Enter your complete address (min 10 characters)")
        self.address_input.setMaximumHeight(70)
        form_layout.addRow(address_label, self.address_input)
        self.address_error = QtWidgets.QLabel("")
        self.address_error.setObjectName("error")
        form_layout.addRow("", self.address_error)

        # Password
        password_label = QtWidgets.QLabel("Password *")
        password_label.setStyleSheet(label_style)
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Create a strong password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(password_label, self.password_input)
        self.password_error = QtWidgets.QLabel("")
        self.password_error.setObjectName("error")
        form_layout.addRow("", self.password_error)

        req_label = QtWidgets.QLabel(
            "Must have: 8+ chars, uppercase, lowercase, number, special char"
        )
        req_label.setStyleSheet("color: #666; font-size: 10px;")
        req_label.setWordWrap(True)
        form_layout.addRow("", req_label)

        # Confirm Password
        confirm_label = QtWidgets.QLabel("Confirm Password *")
        confirm_label.setStyleSheet(label_style)
        self.confirm_password_input = QtWidgets.QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter your password")
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(confirm_label, self.confirm_password_input)
        self.confirm_password_error = QtWidgets.QLabel("")
        self.confirm_password_error.setObjectName("error")
        form_layout.addRow("", self.confirm_password_error)

        card_layout.addLayout(form_layout)

        # Register button
        register_btn = QtWidgets.QPushButton("Register Now")
        register_btn.setObjectName("primary")
        register_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        register_btn.clicked.connect(self.register)
        card_layout.addWidget(register_btn)

        # Login link
        login_link = QtWidgets.QPushButton("Already have an account? Login Now")
        login_link.setObjectName("secondary")
        login_link.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        login_link.clicked.connect(self.show_login)
        card_layout.addWidget(login_link, alignment=QtCore.Qt.AlignCenter)

        main_layout.addWidget(card)
        scroll.setWidget(main_widget)

        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def clear_errors(self):
        self.name_error.setText("")
        self.gender_error.setText("")
        self.email_error.setText("")
        self.mobile_error.setText("")
        self.address_error.setText("")
        self.password_error.setText("")
        self.confirm_password_error.setText("")

    def register(self):
        self.clear_errors()

        full_name = self.name_input.text().strip()
        gender = self.gender_input.currentText()
        email = self.email_input.text().strip().lower()
        mobile = self.mobile_input.text().strip()
        address = self.address_input.toPlainText().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        is_valid = True

        if not full_name:
            self.name_error.setText("Full name is required")
            is_valid = False
        elif not validate_name(full_name):
            self.name_error.setText("Name should contain only letters and spaces")
            is_valid = False

        if gender == "Select Gender":
            self.gender_error.setText("Please select a gender")
            is_valid = False

        if not email:
            self.email_error.setText("Email is required")
            is_valid = False
        elif not validate_email(email):
            self.email_error.setText("Please enter a valid email")
            is_valid = False
        elif email in USERS_DATA:
            self.email_error.setText("Email is already registered")
            is_valid = False

        if not mobile:
            self.mobile_error.setText("Mobile number is required")
            is_valid = False
        elif not validate_mobile(mobile):
            self.mobile_error.setText("Mobile must be exactly 10 digits")
            is_valid = False

        if not address:
            self.address_error.setText("Address is required")
            is_valid = False
        elif len(address) < 10:
            self.address_error.setText("Address must be at least 10 characters")
            is_valid = False

        if not password:
            self.password_error.setText("Password is required")
            is_valid = False
        else:
            valid, msg = validate_password(password)
            if not valid:
                self.password_error.setText(msg)
                is_valid = False

        if password != confirm_password:
            self.confirm_password_error.setText("Passwords do not match")
            is_valid = False

        if not is_valid:
            return

        USERS_DATA[email] = {
            'full_name': full_name,
            'gender': gender,
            'email': email,
            'mobile': mobile,
            'address': address,
            'password': hash_password(password)
        }

        QtWidgets.QMessageBox.information(
            self,
            "Success",
            "Registration successful! Please login."
        )
        self.show_login()

    def show_login(self):
        main_window = self.window()
        if hasattr(main_window, 'show_login'):
            main_window.show_login()


# ------------------- MAIN WINDOW (STACK CONTROLLER) -------------------

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login & Registration System - No Database")

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_window = LoginWindow(self)
        self.register_window = RegistrationWindow(self)

        self.stack.addWidget(self.login_window)
        self.stack.addWidget(self.register_window)

        self.setStyleSheet(GOLD_STYLE)
        self.show_login()

    def show_login(self):
        self.stack.setCurrentWidget(self.login_window)
        self.setFixedSize(500, 550)
        self.center_window()

    def show_register(self):
        self.stack.setCurrentWidget(self.register_window)
        self.setFixedSize(650, 780)
        self.center_window()

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Login & Registration System - No Database")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
