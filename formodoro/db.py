from pymongo import MongoClient
import os
from tinydb import TinyDB


db_implementation = os.environ.get("DB_IMPLEMENTATION", "tinydb")

if db_implementation == "tinydb":
    db = TinyDB(os.environ.get("TINYDB_PATH", "/tinydb/db.json"))
    collection = db.table(os.environ.get("TINYDB_TABLE", "mytable"))

    def insert_data(data: dict):
        collection.insert(data)

elif db_implementation == "mongodb":
    client = MongoClient(os.environ.get("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.environ.get("MONGODB_DB", "mydatabase")]
    collection = db[os.environ.get("MONGODB_COLLECTION", "mycollection")]

    def insert_data(data: dict):
        collection.insert_one(data)

else:
    raise ValueError("Unsupported DB implementation. Use 'tinydb' or 'mongodb'.")
