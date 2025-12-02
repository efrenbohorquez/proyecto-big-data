
import os
from dotenv import load_dotenv
from helpers.mongo_db import Mongo_DB

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

def fix_metadata():
    print("=" * 50)
    print("FIXING METADATA STRUCTURE")
    print("=" * 50)

    mongo = Mongo_DB(MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION)
    collection = mongo.coll
    
    # Find documents without 'metadatos' field
    query = {"metadatos": {"$exists": False}}
    count = collection.count_documents(query)
    
    print(f"Documents missing 'metadatos': {count}")
    
    if count == 0:
        print("All documents have 'metadatos'. Nothing to do.")
        return

    cursor = collection.find(query)
    updated = 0
    
    for doc in cursor:
        doc_id = doc['_id']
        titulo = doc.get('titulo', 'Unknown')
        
        # Extract fields to move to metadatos
        categoria = doc.get('categoria', 'Otros Documentos')
        # Some docs might have 'año' or other fields if they came from other sources, 
        # but our flat script only added 'categoria'.
        
        metadatos = {
            "categoria": categoria,
            "año": None # Default
        }
        
        # Update the document
        # Set metadatos AND unset the flat 'categoria' field to clean up
        collection.update_one(
            {'_id': doc_id},
            {
                '$set': {'metadatos': metadatos},
                '$unset': {'categoria': ""} 
            }
        )
        updated += 1
        print(f"Fixed: {titulo[:30]}...")

    print(f"\nSuccessfully updated {updated} documents.")

if __name__ == "__main__":
    fix_metadata()
