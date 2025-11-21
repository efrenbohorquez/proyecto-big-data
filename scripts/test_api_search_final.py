import requests
import json

url = "http://localhost:5001/api/buscar-avanzada"
# Usar 'query' en lugar de 'q'
params = {
    "query": "justicia",
    "limit": 5
}

try:
    print(f"Testing API: {url}")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Total resultados: {data.get('total', 0)}")
        print(f"✅ Motor usado: {data.get('motor', 'desconocido')}")
        
        # Buscar en 'documentos' o 'resultados'
        documentos = data.get('documentos', data.get('resultados', []))
        
        if documentos:
            print(f"✅ Se encontraron {len(documentos)} documentos")
            doc = documentos[0]
            print(f"   - Título: {doc.get('titulo')}")
            print(f"   - Snippet: {doc.get('snippet')}")
        else:
            print("⚠️ No se encontraron resultados para 'justicia'")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
