"""
Script simplificado para agregar solo los documentos faltantes a MongoDB
Sin eliminar documentos existentes y sin extraer texto completo (evita cuelgues)
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from helpers import Mongo_DB
from datetime import datetime

load_dotenv()

def main():
    print("=" * 70)
    print("AGREGAR DOCUMENTOS FALTANTES A MONGODB")
    print("=" * 70)
    
    # Conectar a MongoDB
    mongo = Mongo_DB(
        os.getenv('MONGO_URI'),
        os.getenv('MONGO_DB', 'proyecto_big_data'),
        os.getenv('MONGO_COLLECTION', 'documentos')
    )
    
    collection = mongo.coll  # Use .coll instead of .db[mongo.collection]
    
    # Obtener el número máximo actual
    max_doc = collection.find_one(sort=[("numero", -1)])
    next_numero = (max_doc['numero'] + 1) if max_doc else 1
    
    print(f"\nDocumentos actuales en BD: {collection.count_documents({})}")
    print(f"Próximo número a asignar: {next_numero}")
    
    # Escanear carpeta de documentos
    uploads_dir = Path("uploads/documentos_procuraduria")
    if not uploads_dir.exists():
        print(f"\n✗ Error: No existe la carpeta {uploads_dir}")
        return
    
    # Obtener archivos
    archivos = list(uploads_dir.glob("*.pdf")) + list(uploads_dir.glob("*.docx"))
    print(f"Archivos encontrados en uploads: {len(archivos)}")
    
    # Obtener títulos ya cargados para evitar duplicados
    titulos_existentes = set()
    for doc in collection.find({}, {"titulo": 1}):
        titulos_existentes.add(doc.get("titulo", ""))
    
    # Agregar documentos nuevos (máximo 10 para no tardar mucho)
    agregados = 0
    objetivo = 10  # Agregar 10 para tener margen
    
    print(f"\nObjetivo: Agregar {objetivo} documentos nuevos")
    print("Procesando...")
    
    for archivo in archivos:
        if agregados >= objetivo:
            break
            
        titulo = archivo.stem
        
        # Saltar si ya existe
        if titulo in titulos_existentes:
            continue
        
        try:
            # Crear documento simple SIN extraer texto completo (para evitar cuelgues)
            doc = {
                "numero": next_numero,
                "titulo": titulo,
                "categoria": "Otros Documentos",
                "tipo": archivo.suffix[1:].upper(),
                "archivo_local": str(archivo.name),
                "ruta_completa": str(archivo),
                "tamano_bytes": archivo.stat().st_size,
                "tamano_mb": round(archivo.stat().st_size / 1024 / 1024, 2),
                "fecha_descarga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fuente": "Procuraduría General de la Nación",
                "texto_contenido": "",  # Vacío por ahora (evita cuelgues)
                "archivo_existe": True,
                "estado": "disponible"
            }
            
            # Insertar
            collection.insert_one(doc)
            agregados += 1
            next_numero += 1
            
            print(f"  ✓ {agregados}. {titulo[:50]}")
            
        except Exception as e:
            print(f"  ✗ Error con {archivo.name}: {e}")
            continue
    
    # Verificar resultado
    total_final = collection.count_documents({})
    
    print("\n" + "=" * 70)
    print("RESULTADO")
    print("=" * 70)
    print(f"  Documentos agregados: {agregados}")
    print(f"  Total en MongoDB: {total_final}")
    print(f"  Objetivo (mínimo 100): {'✅ CUMPLIDO' if total_final >= 100 else '⚠️ FALTA'}")
    print("=" * 70)

if __name__ == "__main__":
    main()
