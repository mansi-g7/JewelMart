"""
database.py
Shared MongoDB connection for JewelMart Project
"""

from pymongo import MongoClient

DEFAULT_URI = "mongodb://localhost:27017/"
DB_NAME = "JewelMart"

_client = None


def get_db():
    """Return main JewelMart database object."""
    global _client
    if _client is None:
        _client = MongoClient(DEFAULT_URI)
    return _client[DB_NAME]


# ------------------ COLLECTIONS ------------------

def get_users_collection():
    """Users registered in the system."""
    return get_db()["users"]


def get_products_collection():
    """Products added by admin."""
    return get_db()["products"]


def get_orders_collection():
    """Orders placed by users."""
    return get_db()["orders"]
