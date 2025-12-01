from PyQt5 import QtWidgets
import sys
import os
import threading

# Prefer a cleaned UI module if present (ui_clean). Fall back to original ui.
try:
    from ui_clean import MainWindow
except Exception:
    from ui import MainWindow

from flask import Flask, render_template, url_for
import json

# import categories/products for templates
try:
    from data import categories, get_products
except Exception:
    categories = []
    def get_products(cat=None):
        return []


SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")


# ------------------------------
# Flask App (Homepage)
# ------------------------------
flask_app = Flask(__name__, static_folder="static", template_folder="templates")


@flask_app.route("/")
def home():
    return render_template("index.html", categories=categories)


@flask_app.route('/contact')
def contact():
    return render_template('contact.html')


@flask_app.route('/about')
def about():
    return render_template('about.html')


@flask_app.route('/categories')
def categories_page():
    return render_template('categories.html', categories=categories)


@flask_app.route('/categories/<name>')
def category_products(name):
    prods = get_products(name)
    return render_template('products.html', category=name, products=prods)


def run_flask():
    # bind to localhost only; set debug False for background thread
    flask_app.run(host='127.0.0.1', debug=False, port=5000, use_reloader=False)


# ------------------------------
# Load / Save Settings (PyQt)
# ------------------------------
def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"theme": "light"}


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def apply_stylesheet(app):
    try:
        settings = load_settings()
        theme = settings.get("theme", "dark")
        qss_name = "style.qss" if theme == "dark" else "style_light.qss"
        qss_path = os.path.join(os.path.dirname(__file__), qss_name)

        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())

    except Exception:
        pass


# ------------------------------
# Main PyQt Application
# ------------------------------
if __name__ == '__main__':

    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app)

    w = MainWindow()

    # Make theme functions available to UI
    try:
        w._load_settings = load_settings
        w._save_settings = save_settings
    except Exception:
        pass

    w.show()
    sys.exit(app.exec_())