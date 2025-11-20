import os
from dotenv import load_dotenv
from helpers import Mongo_DB, ElasticSearch

load_dotenv()

def check_connections():
    print("Verificando conexiones...")
    
    # MongoDB
    print("\n--- MongoDB ---")
    try:
        mongo = Mongo_DB(
            os.getenv('MONGO_URI'),
            os.getenv('MONGO_DB', 'proyecto_big_data'),
            'documentos_procuraduria'
        )
        mongo.probar_conexion()
    except Exception as e:
        print(f"Error MongoDB: {e}")

    # ElasticSearch
    print("\n--- ElasticSearch ---")
    try:
        elastic = ElasticSearch(
            os.getenv('ELASTIC_CLOUD_URL'),
            os.getenv('ELASTIC_API_KEY')
        )
        elastic.probar_conexion()
    except Exception as e:
        print(f"Error ElasticSearch: {e}")

if __name__ == "__main__":
    check_connections()
