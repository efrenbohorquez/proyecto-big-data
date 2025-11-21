# helpers/elasticsearch.py
# Operaciones con ElasticSearch
import logging
import math
from elasticsearch import Elasticsearch
from typing import Optional, Dict, Any, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticSearch:
    def __init__(self, url: str = '', api_key: str = ''):
        self.url = url
        self.api_key = api_key
        self.client: Optional[Elasticsearch] = None
        if url and api_key:
            self._connect()
        else:
            logger.warning("ElasticSearch no configurado. URL o API Key vacíos.")

    def _connect(self):
        """Establece la conexión a ElasticSearch."""
        try:
            if self.url and self.api_key:
                self.client = Elasticsearch(
                    self.url,
                    api_key=self.api_key
                )
                # Verificar conexión
                self.client.info()
                logger.info("Conexión a ElasticSearch exitosa.")
            else:
                logger.warning("URL o API Key de ElasticSearch no configurados.")
        except Exception as e:
            logger.error(f"Error al conectar a ElasticSearch: {e}")
            self.client = None

    def probar_conexion(self) -> bool:
        """Prueba la conexión."""
        try:
            if self.client:
                self.client.info()
                return True
            return False
        except Exception:
            return False

    def buscar_documentos(self, query: str, categoria: str, tipo: str, pagina: int, por_pagina: int, orden: str) -> Dict[str, Any]:
        """
        Búsqueda avanzada usando ElasticSearch.
        Retorna un diccionario con los resultados y metadatos.
        """
        if not self.client:
            raise Exception("Cliente de ElasticSearch no inicializado")

        from_doc = (pagina - 1) * por_pagina
        
        # Construir query de ElasticSearch
        must_clauses = []
        filter_clauses = []
        
        # Query de texto (búsqueda fuzzy para tolerancia a errores)
        if query:
            must_clauses.append({
                'multi_match': {
                    'query': query,
                    'fields': ['titulo^3', 'texto_contenido', 'tipo^2', 'metadatos.categoria'],
                    'fuzziness': 'AUTO',
                    'operator': 'or'
                }
            })
        
        # Filtros
        if categoria:
            filter_clauses.append({'term': {'metadatos.categoria': categoria}})
        if tipo:
            filter_clauses.append({'term': {'tipo.keyword': tipo}})
        
        # Configurar ordenamiento
        sort_config = []
        if orden == 'fecha_desc':
            sort_config = [{'fecha_descarga': {'order': 'desc'}}]
        elif orden == 'fecha_asc':
            sort_config = [{'fecha_descarga': {'order': 'asc'}}]
        elif orden == 'titulo':
            sort_config = [{'titulo.keyword': {'order': 'asc'}}]
        else:  # relevancia (default)
            sort_config = ['_score']
        
        # Ejecutar búsqueda
        es_query = {
            'bool': {
                'must': must_clauses if must_clauses else [{'match_all': {}}],
                'filter': filter_clauses
            }
        }
        
        try:
            resultado = self.client.search(
                index='procuraduria_documentos',
                query=es_query,
                from_=from_doc,
                size=por_pagina,
                sort=sort_config,
                highlight={
                    'fields': {
                        'titulo': {},
                        'tipo': {}
                    }
                }
            )
            
            # Procesar resultados
            documentos = []
            for hit in resultado['hits']['hits']:
                doc = hit['_source']
                doc['_id'] = hit['_id']
                doc['_score'] = hit['_score']
                
                # Agregar highlights si existen
                if 'highlight' in hit:
                    doc['_highlight'] = hit['highlight']
                
                documentos.append(doc)
            
            total = resultado['hits']['total']['value']
            total_paginas = math.ceil(total / por_pagina)
            
            return {
                'exito': True,
                'documentos': documentos,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': total_paginas,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda ElasticSearch: {e}")
            raise e

    def buscar_con_agregaciones(self, query: str, categoria: str, tipo: str, pagina: int, por_pagina: int, orden: str) -> Dict[str, Any]:
        """
        Búsqueda avanzada con agregaciones para filtros dinámicos.
        Incluye conteos por categoría, tipo y año.
        """
        if not self.client:
            raise Exception("Cliente de ElasticSearch no inicializado")

        from_doc = (pagina - 1) * por_pagina
        
        # Construir query
        must_clauses = []
        filter_clauses = []
        
        if query:
            must_clauses.append({
                'multi_match': {
                    'query': query,
                    'fields': ['titulo^3', 'texto_contenido^1', 'tipo^2'],
                    'fuzziness': 'AUTO',
                    'operator': 'or'
                }
            })
        
        if categoria:
            filter_clauses.append({'term': {'metadatos.categoria.keyword': categoria}})
        if tipo:
            filter_clauses.append({'term': {'tipo.keyword': tipo}})
        
        # Configurar ordenamiento
        sort_config = []
        if orden == 'fecha_desc':
            sort_config = [{'fecha_descarga': {'order': 'desc'}}]
        elif orden == 'fecha_asc':
            sort_config = [{'fecha_descarga': {'order': 'asc'}}]
        elif orden == 'titulo':
            sort_config = [{'titulo.keyword': {'order': 'asc'}}]
        else:
            sort_config = ['_score']
        
        # Query con agregaciones
        es_query = {
            'bool': {
                'must': must_clauses if must_clauses else [{'match_all': {}}],
                'filter': filter_clauses
            }
        }
        
        try:
            resultado = self.client.search(
                index='procuraduria_documentos',
                query=es_query,
                from_=from_doc,
                size=por_pagina,
                sort=sort_config,
                highlight={
                    'fields': {
                        'titulo': {
                            'pre_tags': ['<mark>'],
                            'post_tags': ['</mark>']
                        },
                        'texto_contenido': {
                            'fragment_size': 200,
                            'number_of_fragments': 2,
                            'pre_tags': ['<mark>'],
                            'post_tags': ['</mark>']
                        }
                    }
                },
                aggs={
                    'por_categoria': {
                        'terms': {
                            'field': 'metadatos.categoria.keyword',
                            'size': 20
                        }
                    },
                    'por_tipo': {
                        'terms': {
                            'field': 'tipo.keyword',
                            'size': 10
                        }
                    },
                    'por_año': {
                        'terms': {
                            'field': 'metadatos.año',
                            'size': 10,
                            'order': {'_key': 'desc'}
                        }
                    }
                }
            )
            
            # Procesar resultados
            documentos = []
            for hit in resultado['hits']['hits']:
                doc = hit['_source']
                doc['_id'] = hit['_id']
                doc['_score'] = hit['_score']
                
                # Agregar highlights mejorados
                if 'highlight' in hit:
                    # Snippet del texto_contenido
                    if 'texto_contenido' in hit['highlight']:
                        doc['snippet'] = ' ... '.join(hit['highlight']['texto_contenido'])
                    else:
                        # Fallback: usar inicio del texto
                        texto = doc.get('texto_contenido', '')
                        doc['snippet'] = texto[:200] + '...' if len(texto) > 200 else texto
                    
                    # Título resaltado
                    if 'titulo' in hit['highlight']:
                        doc['titulo_resaltado'] = hit['highlight']['titulo'][0]
                else:
                    # Sin highlights
                    texto = doc.get('texto_contenido', '')
                    doc['snippet'] = texto[:200] + '...' if len(texto) > 200 else texto
                
                documentos.append(doc)
            
            total = resultado['hits']['total']['value']
            total_paginas = math.ceil(total / por_pagina)
            
            # Procesar agregaciones
            agregaciones = {}
            if 'aggregations' in resultado:
                aggs = resultado['aggregations']
                
                agregaciones['categorias'] = [
                    {'nombre': bucket['key'], 'count': bucket['doc_count']}
                    for bucket in aggs.get('por_categoria', {}).get('buckets', [])
                ]
                
                agregaciones['tipos'] = [
                    {'nombre': bucket['key'], 'count': bucket['doc_count']}
                    for bucket in aggs.get('por_tipo', {}).get('buckets', [])
                ]
                
                agregaciones['años'] = [
                    {'año': bucket['key'], 'count': bucket['doc_count']}
                    for bucket in aggs.get('por_año', {}).get('buckets', [])
                ]
            
            return {
                'exito': True,
                'documentos': documentos,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': total_paginas,
                'query': query,
                'agregaciones': agregaciones
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda con agregaciones: {e}")
            raise e

    def obtener_sugerencias(self, query: str, limit: int = 5) -> List[str]:
        """
        Obtiene sugerencias de autocompletado basadas en títulos.
        """
        if not self.client or not query:
            return []
        
        try:
            resultado = self.client.search(
                index='procuraduria_documentos',
                query={
                    'match': {
                        'titulo': {
                            'query': query,
                            'fuzziness': 'AUTO'
                        }
                    }
                },
                size=limit,
                _source=['titulo']
            )
            
            sugerencias = []
            for hit in resultado['hits']['hits']:
                titulo = hit['_source'].get('titulo', '')
                if titulo and titulo not in sugerencias:
                    sugerencias.append(titulo)
            
            return sugerencias
            
        except Exception as e:
            logger.error(f"Error al obtener sugerencias: {e}")
            return []
