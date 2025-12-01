from pymongo import MongoClient

DB_URI = "mongodb://localhost:27017/"
DB_NAME = "JewelMart"

def get_db():
    client = MongoClient(DB_URI)
    return client[DB_NAME]

# USERS = register collection
def get_users_collection():
    return get_db()["register"]

# PRODUCTS = jewel_add collection
def get_products_collection():
    return get_db()["jewel_add"]

# ORDERS = order collection
def get_orders_collection():
    return get_db()["order"]

# CATEGORY = category collection
def get_category_collection():
    return get_db()["category"]
