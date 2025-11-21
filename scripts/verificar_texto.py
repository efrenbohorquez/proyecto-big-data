from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB', 'proyecto_big_data')]
collection = db[os.getenv('MONGO_COLLECTION', 'documentos_procuraduria')]

# Buscar documento específico
doc = collection.find_one({'titulo': {'$regex': 'justicia transicional', '$options': 'i'}})

if doc:
    print(f"✅ Documento encontrado: {doc.get('titulo')}")
    texto = doc.get('texto_contenido', '')
    if texto:
        print(f"✅ Tiene texto: {len(texto)} caracteres")
    else:
        print("❌ NO tiene texto todavía")
else:
    print("❌ Documento no encontrado")

# Contar cuántos tienen texto
count = collection.count_documents({'texto_contenido': {'$exists': True, '$ne': ''}})
print(f"📊 Total documentos con texto: {count}")
