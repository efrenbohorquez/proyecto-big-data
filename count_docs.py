import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

try:
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('MONGO_DB')]
    collection = db[os.getenv('MONGO_COLLECTION')]
    count = collection.count_documents({})
    print(f"Total documents: {count}")
except Exception as e:
    print(f"Error counting documents: {e}")
