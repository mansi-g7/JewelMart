"""
database.py
Shared MongoDB connection. Returns the `admin` database under the `JewelMart`
connection.
"""

from pymongo import MongoClient

# Default MongoDB connection string
DEFAULT_URI = "mongodb://localhost:27017/"

# Database name
DB_NAME = "JewelMart"

# Admin namespace (collection group)
ADMIN_NS = "admin"

# Singleton client instance
_client = None


def get_admin_db(uri: str = DEFAULT_URI):
    """
    Return the admin database object:
    client[DB_NAME][ADMIN_NS]

    • Creates MongoClient only once (singleton)
    • Reuses connection across modules
    """

    global _client

    # Create client only once
    if _client is None:
        _client = MongoClient(uri)

    # Return JewelMart.admin namespace
    return _client[DB_NAME][ADMIN_NS]
