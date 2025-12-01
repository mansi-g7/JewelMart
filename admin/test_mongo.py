from pymongo import MongoClient
import sys

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    info = client.server_info()
    print("OK", info.get("version"))
except Exception as e:
    print("ERR", repr(e))
    sys.exit(1)
