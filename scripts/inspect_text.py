from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB', 'proyecto_big_data')]
collection = db[os.getenv('MONGO_COLLECTION', 'documentos_procuraduria')]

# Buscar documentos con texto
docs = list(collection.find({'texto_contenido': {'$exists': True, '$ne': ''}}).limit(5))

if docs:
    print(f"✅ Se encontraron {len(docs)} documentos con texto")
    doc = docs[0]
    print(f"   - Título: {doc.get('titulo')}")
    texto = doc.get('texto_contenido', '')
    print(f"   - Longitud: {len(texto)}")
    print(f"   - Muestra (primeros 500 chars):\n{texto[:500]}")
    
    # Verificar si 'justicia' está en el texto
    if 'justicia' in texto.lower():
        print("\n✅ La palabra 'justicia' ESTÁ en el texto")
    else:
        print("\n❌ La palabra 'justicia' NO está en el texto")
        
    # Verificar si 'colombia' está en el texto
    if 'colombia' in texto.lower():
        print("✅ La palabra 'colombia' ESTÁ en el texto")
    else:
        print("❌ La palabra 'colombia' NO está en el texto")
else:
    print("❌ No hay documentos con texto")
