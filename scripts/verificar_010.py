from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB', 'proyecto_big_data')]
collection = db[os.getenv('MONGO_COLLECTION', 'documentos_procuraduria')]

# Buscar documento 010
doc = collection.find_one({'titulo': {'$regex': '010'}})

if doc:
    print(f"✅ Documento encontrado: {doc.get('titulo')}")
    texto = doc.get('texto_contenido', '')
    if texto:
        print(f"✅ Tiene texto: {len(texto)} caracteres")
        print(f"   Muestra: {texto[:100]}...")
    else:
        print("❌ NO tiene texto todavía")
else:
    print("❌ Documento 010 no encontrado")
