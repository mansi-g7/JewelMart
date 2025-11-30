"""Serve the Flask app with Waitress (production WSGI server).

Usage:
  pip install waitress
  python run_flask_prod.py

This avoids the Werkzeug "development server" warning and is suitable
for local/Windows production testing.
"""
from waitress import serve
from app import flask_app


if __name__ == "__main__":
    # listen on localhost:5000
    serve(flask_app, host='127.0.0.1', port=5000)
