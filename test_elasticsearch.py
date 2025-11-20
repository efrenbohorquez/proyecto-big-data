from helpers import ElasticSearch
from dotenv import load_dotenv
import os

load_dotenv()

es = ElasticSearch(os.getenv('ELASTIC_CLOUD_URL'), os.getenv('ELASTIC_API_KEY'))
es.probar_conexion()

# Verificar documentos indexados
index_name = 'procuraduria_documentos'
resultado = es.client.count(index=index_name)
print(f'Total documentos en ElasticSearch: {resultado["count"]}')

# Buscar documentos de ejemplo
print('\nPrimeros 3 documentos:')
busqueda = es.client.search(index=index_name, size=3, query={'match_all': {}})
for i, doc in enumerate(busqueda['hits']['hits'], 1):
    source = doc['_source']
    titulo = source['titulo'][:60]
    tamano = source['tamano_mb']
    categoria = source['metadatos']['categoria']
    print(f'{i}. {titulo}... ({tamano:.2f} MB) - {categoria}')

# Búsqueda por texto
print('\nBúsqueda: "manual"')
busqueda = es.client.search(
    index=index_name, 
    size=3,
    query={'match': {'titulo': 'manual'}}
)
total = busqueda['hits']['total']['value']
print(f'Encontrados: {total} documentos')
for i, doc in enumerate(busqueda['hits']['hits'], 1):
    source = doc['_source']
    titulo = source['titulo'][:60]
    print(f'{i}. {titulo}...')

# Agregación por categoría
print('\nDocumentos por categoría:')
agg_result = es.client.search(
    index=index_name,
    size=0,
    aggs={
        'por_categoria': {
            'terms': {
                'field': 'metadatos.categoria',
                'size': 10
            }
        }
    }
)
for bucket in agg_result['aggregations']['por_categoria']['buckets']:
    print(f"  {bucket['key']}: {bucket['doc_count']}")
