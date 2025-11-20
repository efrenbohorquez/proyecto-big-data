import os

from dotenv import load_dotenv

from helpers import Mongo_DB

load_dotenv()

mongo = Mongo_DB(os.getenv('MONGO_URI'), os.getenv('MONGO_DB'), os.getenv('MONGO_COLLECTION'))
stats = mongo.obtener_estadisticas()

print("="*60)
print("ESTADÍSTICAS DE LA BASE DE DATOS")
print("="*60)
print(f"Total documentos: {stats['total_documentos']}")
print(f"Número de categorías: {len(stats['categorias'])}")
print(f"Tipos de archivo: {stats['tipos']}")
print(f"Tamaño total: {stats['tamano_total']:.2f} MB")
print("\nCategorías:")
for cat in stats['categorias'][:5]:
    print(f"  - {cat['nombre']}: {cat['cantidad']} docs")
print("="*60)
