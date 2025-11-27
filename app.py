from PyQt5 import QtWidgets
# Prefer a cleaned UI module if present (ui_clean). Fall back to original ui.
try:
    from ui_clean import MainWindow
except Exception:
    from ui import MainWindow
# import sys
# import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")


def load_settings():
    try:
        import json
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"theme": "dark"}


def save_settings(settings):
    try:
        import json
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app)
    w = MainWindow()
    # expose settings helpers to the window so UI can toggle theme
    try:
        w._load_settings = load_settings
        w._save_settings = save_settings
    except Exception:
        pass
    w.show()
    sys.exit(app.exec_())
