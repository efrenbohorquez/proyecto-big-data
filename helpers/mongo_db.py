# helpers/mongo_db.py
# Operaciones CRUD en MongoDB
import logging
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Mongo_DB:
    def __init__(self, uri: str, db_name: str = 'proyecto_big_data', collection: str = 'documentos'):
        if not uri:
            raise ValueError("URI de MongoDB no puede estar vacío")
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection
        self.client: Optional[MongoClient] = None
        self.db = None
        self.coll = None
        self._connect()

    def _connect(self):
        """Establece la conexión a MongoDB."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[self.db_name]
            self.coll = self.db[self.collection_name]
            # Verificar conexión
            self.client.admin.command('ping')
            logger.info("Conexión a MongoDB exitosa.")
        except ConnectionFailure:
            logger.error("Error de conexión a MongoDB: No se pudo conectar al servidor.")
        except Exception as e:
            logger.error(f"Error al conectar a MongoDB: {e}")

    def probar_conexion(self) -> bool:
        """Prueba la conexión a la base de datos."""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de la colección."""
        try:
            total_docs = self.coll.count_documents({})
            
            # Categorías
            pipeline_cat = [
                {'$group': {'_id': '$metadatos.categoria', 'cantidad': {'$sum': 1}}},
                {'$sort': {'cantidad': -1}}
            ]
            categorias = list(self.coll.aggregate(pipeline_cat))
            
            # Tipos
            tipos = self.coll.distinct('tipo')
            
            # Tamaño total (simulado si no existe el campo)
            tamano_total = sum([doc.get('tamano_mb', 0) for doc in self.coll.find({}, {'tamano_mb': 1})])

            return {
                'total_documentos': total_docs,
                'categorias': [{'nombre': c['_id'], 'cantidad': c['cantidad']} for c in categorias if c['_id']],
                'tipos': tipos,
                'tamano_total': tamano_total
            }
        except PyMongoError as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {'total_documentos': 0, 'categorias': [], 'tipos': [], 'tamano_total': 0}

    def buscar_documentos(self, query: str, categoria: str, tipo: str, skip: int, limit: int, sort_config: List[tuple]) -> tuple[List[Dict], int]:
        """Busca documentos con filtros y paginación."""
        try:
            filtro = {}
            if query:
                filtro['$or'] = [
                    {'titulo': {'$regex': query, '$options': 'i'}},
                    {'texto_contenido': {'$regex': query, '$options': 'i'}},
                    {'tipo': {'$regex': query, '$options': 'i'}},
                    {'metadatos.categoria': {'$regex': query, '$options': 'i'}}
                ]
            if categoria:
                filtro['metadatos.categoria'] = categoria
            if tipo:
                filtro['tipo'] = tipo

            cursor = self.coll.find(filtro).sort(sort_config).skip(skip).limit(limit)
            documentos = list(cursor)
            total = self.coll.count_documents(filtro)
            
            # Convertir ObjectId a string
            for doc in documentos:
                doc['_id'] = str(doc['_id'])
                
            return documentos, total
        except PyMongoError as e:
            logger.error(f"Error en búsqueda: {e}")
            return [], 0

    def obtener_documento_por_numero(self, numero: int) -> Optional[Dict]:
        """Obtiene un documento por su número identificador."""
        try:
            doc = self.coll.find_one({'numero': numero})
            if doc:
                doc['_id'] = str(doc['_id'])
            return doc
        except PyMongoError as e:
            logger.error(f"Error al obtener documento {numero}: {e}")
            return None

    def obtener_documentos_recientes(self, limite: int = 10) -> List[Dict]:
        """Obtiene los documentos más recientes."""
        try:
            docs = list(self.coll.find().sort('fecha_descarga', -1).limit(limite))
            for doc in docs:
                doc['_id'] = str(doc['_id'])
            return docs
        except PyMongoError as e:
            logger.error(f"Error al obtener recientes: {e}")
            return []

    def obtener_estadisticas_avanzadas(self) -> Dict[str, Any]:
        """Obtiene estadísticas avanzadas para el dashboard."""
        try:
            # Categorías y tamaño
            pipeline_cat = [
                {
                    '$group': {
                        '_id': '$metadatos.categoria',
                        'cantidad': {'$sum': 1},
                        'tamano_total_mb': {'$sum': '$tamano_mb'}
                    }
                },
                {'$sort': {'cantidad': -1}}
            ]
            categorias_stats = list(self.coll.aggregate(pipeline_cat))

            # Tipos
            pipeline_tipo = [
                {'$group': {'_id': '$tipo', 'cantidad': {'$sum': 1}}},
                {'$sort': {'cantidad': -1}}
            ]
            tipos_stats = list(self.coll.aggregate(pipeline_tipo))

            # Años
            pipeline_anos = [
                {'$match': {'metadatos.año': {'$ne': None}}},
                {'$group': {'_id': '$metadatos.año', 'cantidad': {'$sum': 1}}},
                {'$sort': {'_id': -1}}
            ]
            anos_stats = list(self.coll.aggregate(pipeline_anos))

            return {
                'categorias': categorias_stats,
                'tipos': tipos_stats,
                'años': anos_stats
            }
        except PyMongoError as e:
            logger.error(f"Error en estadísticas avanzadas: {e}")
            return {}
