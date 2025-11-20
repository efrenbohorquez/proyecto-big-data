"""
Script para cargar documentos de Procuraduría a MongoDB y ElasticSearch
Autor: Efren Bohorquez Vargas
Universidad Central
Fecha: 19 de noviembre de 2025

Este script lee los metadatos de los documentos scrapeados y los carga
tanto en MongoDB como en ElasticSearch para análisis Big Data
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from helpers import Mongo_DB, ElasticSearch, Funciones

load_dotenv()

class CargadorDocumentos:
    """
    Clase para cargar documentos a MongoDB y ElasticSearch
    """
    
    def __init__(self):
        # Inicializar conexiones
        self.mongo = Mongo_DB(
            os.getenv('MONGO_URI'),
            os.getenv('MONGO_DB', 'proyecto_big_data'),
            'documentos_procuraduria'  # Nueva colección
        )
        
        self.elastic = ElasticSearch(
            os.getenv('ELASTIC_CLOUD_URL'),
            os.getenv('ELASTIC_API_KEY')
        )
        
        self.funciones = Funciones()
        self.estadisticas = {
            "inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "docs_mongodb": 0,
            "docs_elasticsearch": 0,
            "errores": []
        }
    
    def verificar_conexiones(self):
        """
        Verifica que las conexiones a MongoDB y ElasticSearch funcionen
        """
        print("="*70)
        print("VERIFICANDO CONEXIONES")
        print("="*70)
        
        # Verificar MongoDB
        print("\n1. MongoDB Atlas:")
        try:
            self.mongo.probar_conexion()
            print("   ✓ Conexión exitosa")
        except Exception as e:
            print(f"   ✗ Error de conexión: {str(e)}")
            return False
        
        # Verificar ElasticSearch
        print("\n2. ElasticSearch Cloud:")
        try:
            self.elastic.probar_conexion()
            print("   ✓ Conexión exitosa")
        except Exception as e:
            print(f"   ✗ Error de conexión: {str(e)}")
            return False
        
        return True
    
    def leer_metadatos_scraping(self):
        """
        Lee el archivo JSON con los metadatos del scraping
        """
        print("\n" + "="*70)
        print("LEYENDO METADATOS DE SCRAPING")
        print("="*70)
        
        archivo_json = "uploads/procuraduria_documentos_masivos_20251119_115532.json"
        
        if not os.path.exists(archivo_json):
            print(f"✗ Archivo no encontrado: {archivo_json}")
            return None
        
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"✓ Archivo leído correctamente")
        print(f"✓ Documentos encontrados en JSON: {len(datos['documentos_descargados'])}")
        
        return datos
    
    def preparar_documento_para_bd(self, doc, indice):
        """
        Prepara un documento para ser insertado en las bases de datos
        """
        # Verificar si el archivo existe
        ruta_archivo = doc.get('ruta', '')
        archivo_existe = os.path.exists(ruta_archivo)
        
        # Extraer texto del archivo
        texto_contenido = ""
        if archivo_existe:
            try:
                texto_contenido = self.funciones.extraer_texto_archivo(ruta_archivo) or ""
                if texto_contenido:
                    print(f"  ✓ Texto extraído: {len(texto_contenido)} caracteres")
            except Exception as e:
                print(f"  ✗ Error extrayendo texto: {e}")

        documento = {
            "numero": indice,
            "titulo": doc.get('titulo', 'Sin título'),
            "tipo": doc.get('tipo', 'PDF'),
            "url_original": doc.get('url_original', ''),
            "archivo_local": doc.get('archivo', ''),
            "ruta_completa": ruta_archivo,
            "tamano_bytes": int(doc.get('tamano_bytes', 0)),
            "tamano_mb": float(round(doc.get('tamano_bytes', 0) / 1024 / 1024, 2)),
            "archivo_existe": archivo_existe,
            "texto_contenido": texto_contenido,  # Nuevo campo
            "fecha_descarga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fuente": "Procuraduría General de la Nación",
            "proyecto": "Big Data - Universidad Central",
            "estado": "disponible" if archivo_existe else "error",
            "metadatos": {
                "extension": doc.get('tipo', 'PDF').lower(),
                "categoria": self._determinar_categoria(doc.get('titulo', '')),
                "año": self._extraer_año(doc.get('titulo', ''))
            }
        }
        
        return documento
    
    def _determinar_categoria(self, titulo):
        """
        Determina la categoría del documento según su título
        """
        titulo_lower = titulo.lower()
        
        if any(palabra in titulo_lower for palabra in ['manual', 'funciones', 'procedimiento']):
            return "Manuales y Procedimientos"
        elif any(palabra in titulo_lower for palabra in ['resolución', 'resolucion']):
            return "Resoluciones"
        elif any(palabra in titulo_lower for palabra in ['código', 'codigo', 'disciplinario']):
            return "Códigos y Normatividad"
        elif any(palabra in titulo_lower for palabra in ['informe', 'vigilancia', 'gestión']):
            return "Informes de Gestión"
        elif any(palabra in titulo_lower for palabra in ['procurando', 'boletín', 'boletin']):
            return "Boletines y Publicaciones"
        elif any(palabra in titulo_lower for palabra in ['guía', 'guia', 'cartilla', 'protocolo']):
            return "Guías y Protocolos"
        else:
            return "Otros Documentos"
    
    def _extraer_año(self, titulo):
        """
        Extrae el año del título si existe
        """
        import re
        años = re.findall(r'20\d{2}', titulo)
        return int(años[0]) if años else None
    
    def cargar_a_mongodb(self, documentos):
        """
        Carga los documentos a MongoDB
        """
        print("\n" + "="*70)
        print("CARGANDO DOCUMENTOS A MONGODB")
        print("="*70)
        
        try:
            # Limpiar colección existente (opcional)
            print("\n¿Limpiar colección existente? (Eliminando documentos previos)")
            coleccion = self.mongo.db[self.mongo.collection]
            count_anterior = coleccion.count_documents({})
            
            if count_anterior > 0:
                print(f"Eliminando {count_anterior} documentos existentes...")
                coleccion.delete_many({})
            
            # Insertar documentos
            print(f"\nInsertando {len(documentos)} documentos...")
            
            if documentos:
                resultado = coleccion.insert_many(documentos)
                self.estadisticas["docs_mongodb"] = len(resultado.inserted_ids)
                
                print(f"✓ {len(resultado.inserted_ids)} documentos insertados en MongoDB")
                print(f"✓ Colección: {self.mongo.collection}")
                print(f"✓ Base de datos: {self.mongo.db_name}")
                
                # Crear índices para búsquedas rápidas
                print("\nCreando índices...")
                coleccion.create_index("titulo")
                coleccion.create_index("tipo")
                coleccion.create_index("metadatos.categoria")
                coleccion.create_index("fecha_descarga")
                print("✓ Índices creados")
                
                return True
            else:
                print("✗ No hay documentos para insertar")
                return False
                
        except Exception as e:
            print(f"✗ Error al cargar a MongoDB: {str(e)}")
            self.estadisticas["errores"].append(f"MongoDB: {str(e)}")
            return False
    
    def cargar_a_elasticsearch(self, documentos):
        """
        Indexa los documentos en ElasticSearch
        """
        print("\n" + "="*70)
        print("INDEXANDO DOCUMENTOS EN ELASTICSEARCH")
        print("="*70)
        
        index_name = "procuraduria_documentos"
        
        try:
            # Verificar si el índice existe, si no, crearlo
            if not self.elastic.client.indices.exists(index=index_name):
                print(f"\nCreando índice '{index_name}'...")
                
                # Configuración del índice con mappings
                mapping = {
                    "mappings": {
                        "properties": {
                            "numero": {"type": "integer"},
                            "titulo": {"type": "text", "analyzer": "spanish"},
                            "texto_contenido": {"type": "text", "analyzer": "spanish"},  # Nuevo campo
                            "tipo": {"type": "keyword"},
                            "url_original": {"type": "keyword"},
                            "archivo_local": {"type": "keyword"},
                            "tamano_bytes": {"type": "long"},
                            "tamano_mb": {"type": "float"},
                            "fecha_descarga": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"},
                            "fuente": {"type": "text"},
                            "estado": {"type": "keyword"},
                            "metadatos": {
                                "properties": {
                                    "categoria": {"type": "keyword"},
                                    "año": {"type": "integer"},
                                    "extension": {"type": "keyword"}
                                }
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    }
                }
                
                self.elastic.client.indices.create(index=index_name, body=mapping)
                print(f"✓ Índice '{index_name}' creado")
            else:
                print(f"✓ Índice '{index_name}' ya existe")
            
            # Indexar documentos
            print(f"\nIndexando {len(documentos)} documentos...")
            
            exitosos = 0
            errores = 0
            
            for i, doc in enumerate(documentos, 1):
                try:
                    # Agregar ID único
                    doc_id = f"doc_{doc['numero']}"
                    
                    # Crear copia del documento sin problemas de serialización
                    doc_limpio = {
                        "numero": int(doc['numero']),
                        "titulo": str(doc['titulo']),
                        "texto_contenido": str(doc.get('texto_contenido', '')),  # Nuevo campo
                        "tipo": str(doc['tipo']),
                        "url_original": str(doc['url_original']),
                        "archivo_local": str(doc['archivo_local']),
                        "ruta_completa": str(doc['ruta_completa']),
                        "tamano_bytes": int(doc['tamano_bytes']),
                        "tamano_mb": float(doc['tamano_bytes']) / 1024.0 / 1024.0,
                        "archivo_existe": bool(doc['archivo_existe']),
                        "fecha_descarga": str(doc['fecha_descarga']),
                        "fuente": str(doc['fuente']),
                        "proyecto": str(doc['proyecto']),
                        "estado": str(doc['estado']),
                        "metadatos": {
                            "extension": str(doc['metadatos']['extension']),
                            "categoria": str(doc['metadatos']['categoria']),
                            "año": int(doc['metadatos']['año']) if doc['metadatos']['año'] else None
                        }
                    }
                    
                    self.elastic.client.index(
                        index=index_name,
                        id=doc_id,
                        document=doc_limpio
                    )
                    
                    exitosos += 1
                    
                    if i % 10 == 0:
                        print(f"  Progreso: {i}/{len(documentos)} documentos indexados")
                    
                except Exception as e:
                    errores += 1
                    print(f"  ✗ Error en documento {i}: {str(e)}")
            
            self.estadisticas["docs_elasticsearch"] = exitosos
            
            print(f"\n✓ Indexación completada")
            print(f"  - Exitosos: {exitosos}")
            print(f"  - Errores: {errores}")
            print(f"  - Índice: {index_name}")
            
            # Refrescar índice para que los documentos sean buscables inmediatamente
            self.elastic.client.indices.refresh(index=index_name)
            print("✓ Índice actualizado y listo para búsquedas")
            
            return True
            
        except Exception as e:
            print(f"✗ Error al indexar en ElasticSearch: {str(e)}")
            self.estadisticas["errores"].append(f"ElasticSearch: {str(e)}")
            return False
    
    def generar_reporte_carga(self):
        """
        Genera un reporte del proceso de carga
        """
        print("\n" + "="*70)
        print("REPORTE DE CARGA")
        print("="*70)
        
        self.estadisticas["fin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n📊 RESUMEN:")
        print(f"  Inicio: {self.estadisticas['inicio']}")
        print(f"  Fin: {self.estadisticas['fin']}")
        print(f"\n📁 MONGODB:")
        print(f"  Documentos cargados: {self.estadisticas['docs_mongodb']}")
        print(f"  Base de datos: proyecto_big_data")
        print(f"  Colección: documentos_procuraduria")
        print(f"\n🔍 ELASTICSEARCH:")
        print(f"  Documentos indexados: {self.estadisticas['docs_elasticsearch']}")
        print(f"  Índice: procuraduria_documentos")
        
        if self.estadisticas["errores"]:
            print(f"\n⚠ ERRORES ({len(self.estadisticas['errores'])}):")
            for error in self.estadisticas["errores"]:
                print(f"  - {error}")
        else:
            print(f"\n✓ Sin errores")
        
        # Guardar reporte en JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_reporte = f"uploads/reporte_carga_bd_{timestamp}.json"
        
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(self.estadisticas, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Reporte guardado en: {archivo_reporte}")
        print("="*70)
    
    def ejecutar_carga_completa(self):
        """
        Ejecuta el proceso completo de carga
        """
        print("\n" + "="*70)
        print("CARGA DE DOCUMENTOS A BASES DE DATOS")
        print("Universidad Central - Proyecto Big Data")
        print("Autor: Efren Bohorquez Vargas")
        print("="*70)
        print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Verificar conexiones
        if not self.verificar_conexiones():
            print("\n✗ Error en las conexiones. Proceso cancelado.")
            return False
        
        # 2. Leer metadatos
        datos_scraping = self.leer_metadatos_scraping()
        if not datos_scraping:
            print("\n✗ No se pudieron leer los metadatos. Proceso cancelado.")
            return False
        
        # 3. Preparar documentos
        print("\n" + "="*70)
        print("PREPARANDO DOCUMENTOS")
        print("="*70)
        
        documentos = []
        for i, doc in enumerate(datos_scraping['documentos_descargados'], 1):
            doc_preparado = self.preparar_documento_para_bd(doc, i)
            documentos.append(doc_preparado)
        
        print(f"✓ {len(documentos)} documentos preparados")
        
        # Mostrar estadísticas por categoría
        categorias = {}
        for doc in documentos:
            cat = doc['metadatos']['categoria']
            categorias[cat] = categorias.get(cat, 0) + 1
        
        print(f"\nDistribución por categoría:")
        for cat, cant in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {cant}")
        
        # 4. Cargar a MongoDB
        if not self.cargar_a_mongodb(documentos):
            print("\n⚠ Error al cargar a MongoDB, pero continuando...")
        
        # 5. Indexar en ElasticSearch
        if not self.cargar_a_elasticsearch(documentos):
            print("\n⚠ Error al indexar en ElasticSearch, pero continuando...")
        
        # 6. Generar reporte
        self.generar_reporte_carga()
        
        print("\n" + "="*70)
        print("✓ PROCESO COMPLETADO")
        print("="*70)
        print("\nLos documentos están ahora disponibles para:")
        print("  1. Consultas en MongoDB")
        print("  2. Búsquedas en ElasticSearch")
        print("  3. Visualización en la aplicación Flask")
        print("="*70 + "\n")
        
        return True


def main():
    """
    Función principal
    """
    try:
        cargador = CargadorDocumentos()
        cargador.ejecutar_carga_completa()
        
    except KeyboardInterrupt:
        print("\n\n✗ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
