"""
Script simplificado para cargar solo los documentos nuevos a MongoDB
"""
import os
from dotenv import load_dotenv
from helpers.mongo_db import MongoDB
from helpers.funciones import Funciones
from pathlib import Path

load_dotenv()

def main():
    print("=" * 70)
    print("CARGA RÁPIDA DE DOCUMENTOS NUEVOS")
    print("=" * 70)
    
    # Conectar a MongoDB
    mongo = MongoDB()
    funciones = Funciones()
    
    collection = mongo.get_collection()
    
    # Obtener IDs ya existentes
    existing_ids = set()
    for doc in collection.find({}, {"numero": 1}):
        existing_ids.add(doc.get("numero"))
    
    print(f"\nDocumentos existentes en BD: {len(existing_ids)}")
    
    # Escanear carpeta uploads
    uploads_path = Path("uploads/documentos_procuraduria")
    files = list(uploads_path.glob("*.pdf")) + list(uploads_path.glob("*.docx"))
    
    print(f"Archivos encontrados: {len(files)}")
    
    nuevos = 0
    for idx, file_path in enumerate(files, 1):
        numero = idx + len(existing_ids)
        
        # Solo procesar si el nuevos
        if numero not in existing_ids:
            try:
                texto = funciones.extraer_texto_pdf(str(file_path)) if file_path.suffix == '.pdf' else funciones.extraer_texto_docx(str(file_path))
                
                doc = {
                    "numero": numero,
                    "titulo": file_path.stem,
                    "categoria": "Otros Documentos",
                    "tipo": file_path.suffix[1:].upper(),
                    "archivo_local": str(file_path),
                    "texto_contenido": texto[:5000] if texto else "",  # Primeros 5000 caracteres
                    "tamano_bytes": file_path.stat().st_size
                }
                
                collection.insert_one(doc)
                nuevos += 1
                print(f"  ✓ {nuevos}. {file_path.name}")
                
            except Exception as e:
                print(f"  ✗ Error con {file_path.name}: {e}")
                continue
    
    print(f"\n✓ Nuevos documentos cargados: {nuevos}")
    print(f"✓ Total en BD: {collection.count_documents({})}")

if __name__ == "__main__":
    main()
