import requests
import json

url = "http://localhost:5001/api/buscar-avanzada"
# Probar con una palabra muy común
params = {
    "q": "colombia",
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
        
        resultados = data.get('resultados', [])
        if resultados:
            print(f"✅ Se encontraron {len(resultados)} documentos")
            doc = resultados[0]
            print(f"   - Título: {doc.get('titulo')}")
            print(f"   - Snippet: {doc.get('snippet')}")
        else:
            print("⚠️ No se encontraron resultados para 'colombia'")
            
            # Intentar búsqueda vacía para ver si trae algo
            print("   Intentando búsqueda vacía...")
            response = requests.get(url, params={"q": "", "limit": 5})
            data = response.json()
            resultados = data.get('resultados', [])
            if resultados:
                print(f"   ✅ Búsqueda vacía trajo {len(resultados)} documentos")
                print(f"   - Título: {resultados[0].get('titulo')}")
                print(f"   - Snippet: {resultados[0].get('snippet')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
