"""database.py
 Shared MongoDB connection. Returns the `admin` database under the `JewelMart` 
connection.
 """
 from pymongo import MongoClient
 DEFAULT_URI = "mongodb://localhost:27017/"
 DB_NAME = "JewelMart"
 ADMIN_NS = "admin"
 _client = None
 def get_admin_db(uri: str = DEFAULT_URI):
 """Return the admin database object: client[DB_NAME][ADMIN_NS]
    Singleton client is used so multiple modules reuse the same connection.
    """
 global _client
 if _client is None:
 _client = MongoClient(uri)
 return _client[DB_NAME][ADMIN_NS]