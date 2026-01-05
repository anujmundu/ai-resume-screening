import os
from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI")
mongo_db = os.getenv("MONGO_DB")
mongo_collection = os.getenv("MONGO_COLLECTION")

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

def store_result(result: dict) -> str:
    """
    Insert the result document and return its string id.
    """
    inserted = collection.insert_one(result)
    print("DEBUG: Stored result in MongoDB with _id:", inserted.inserted_id)
    return str(inserted.inserted_id)
