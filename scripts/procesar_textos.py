"""
Script para procesar y extraer texto de los documentos PDF descargados.
Actualiza la base de datos MongoDB con el contenido extraído.
"""
import os
import sys
import PyPDF2
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import time

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

def extraer_texto_pdf(ruta_archivo):
    """Extrae el texto de un archivo PDF."""
    try:
        texto = ""
        with open(ruta_archivo, 'rb') as archivo:
            lector = PyPDF2.PdfReader(archivo)
            num_paginas = len(lector.pages)
            
            print(f"   - Procesando {num_paginas} páginas...")
            
            for i, pagina in enumerate(lector.pages):
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n\n"
                    
        return texto.strip()
    except Exception as e:
        print(f"   ❌ Error al leer PDF: {e}")
        return None

def descargar_archivo(url, ruta_destino):
    """Descarga un archivo si no existe."""
    try:
        print(f"   - Descargando de: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            with open(ruta_destino, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"   ❌ Error descarga: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error descarga: {e}")
        return False

def procesar_documentos():
    # Configuración MongoDB
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB = os.getenv('MONGO_DB', 'proyecto_big_data')
    MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'documentos_procuraduria')
    
    if not MONGO_URI:
        print("❌ Error: MONGO_URI no configurado")
        return

    print(f"🔌 Conectando a MongoDB...")
    print(f"   - Base de datos: {MONGO_DB}")
    print(f"   - Colección: {MONGO_COLLECTION}")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Obtener documentos sin texto o todos
        total_docs = collection.count_documents({})
        print(f"📊 Total documentos en BD: {total_docs}")
        
        cursor = collection.find({})
        
        procesados = 0
        actualizados = 0
        errores = 0
        
        for doc in cursor:
            procesados += 1
            titulo = doc.get('titulo', 'Sin título')
            print(f"\n[{procesados}/{total_docs}] Procesando: {titulo[:50]}...")
            
            # Verificar si ya tiene texto
            if doc.get('texto_contenido') and len(doc.get('texto_contenido')) > 100:
                print("   ✓ Ya tiene contenido de texto. Saltando.")
                continue
                
            # Obtener ruta del archivo
            ruta_relativa = doc.get('ruta_completa')
            if not ruta_relativa:
                # Intentar construir ruta si no existe
                nombre_archivo = doc.get('archivo_local')
                if nombre_archivo:
                    ruta_relativa = os.path.join("uploads", "documentos_procuraduria", nombre_archivo)
                else:
                    print("   ❌ No hay ruta de archivo ni nombre local")
                    errores += 1
                    continue
            
            # Corregir ruta si es necesario (eliminar prefijos extraños si los hay)
            if ruta_relativa.startswith('/') or ruta_relativa.startswith('\\'):
                ruta_relativa = ruta_relativa[1:]
                
            ruta_absoluta = os.path.abspath(ruta_relativa)
            
            # Verificar si existe el archivo
            if not os.path.exists(ruta_absoluta):
                print(f"   ⚠️ Archivo no encontrado localmente: {ruta_relativa}")
                
                # Intentar descargar si tiene URL
                url = doc.get('url_original')
                if url:
                    print("   ⬇️ Intentando descargar...")
                    if descargar_archivo(url, ruta_absoluta):
                        print("   ✅ Descarga exitosa")
                    else:
                        print("   ❌ No se pudo descargar")
                        errores += 1
                        continue
                else:
                    print("   ❌ No hay URL para descargar")
                    errores += 1
                    continue
            
            # Extraer texto
            texto = extraer_texto_pdf(ruta_absoluta)
            
            if texto:
                longitud = len(texto)
                print(f"   ✅ Texto extraído: {longitud} caracteres")
                
                # Actualizar MongoDB
                collection.update_one(
                    {'_id': doc['_id']},
                    {
                        '$set': {
                            'texto_contenido': texto,
                            'procesado_texto': True,
                            'fecha_procesamiento': time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                )
                actualizados += 1
            else:
                print("   ⚠️ No se pudo extraer texto (posible imagen o PDF protegido)")
                errores += 1
                
        print("\n" + "="*50)
        print("RESUMEN DEL PROCESO")
        print("="*50)
        print(f"Total procesados: {procesados}")
        print(f"Actualizados con texto: {actualizados}")
        print(f"Errores/Sin texto: {errores}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    procesar_documentos()
