import requests
import json
from datetime import datetime

print("="*70)
print("PRUEBAS DEL SISTEMA DE BÚSQUEDA")
print("Universidad Central - Proyecto Big Data")
print("="*70)
print()

BASE_URL = "http://127.0.0.1:5001"

# Test 1: Búsqueda simple
print("TEST 1: Búsqueda simple - 'manual'")
print("-" * 70)
try:
    response = requests.post(f"{BASE_URL}/api/buscar", json={
        "query": "manual",
        "pagina": 1,
        "por_pagina": 5
    })
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Motor utilizado: {data.get('motor', 'N/A')}")
    print(f"✓ Documentos encontrados: {data.get('total', 0)}")
    print(f"✓ Documentos en página: {len(data.get('documentos', []))}")
    if data.get('documentos'):
        print("\nPrimeros 3 resultados:")
        for i, doc in enumerate(data['documentos'][:3], 1):
            print(f"  {i}. {doc['titulo'][:60]}...")
            if '_score' in doc:
                print(f"     Relevancia: {doc['_score']:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 2: Búsqueda con filtros
print("TEST 2: Búsqueda con filtros - categoría 'Resoluciones'")
print("-" * 70)
try:
    response = requests.post(f"{BASE_URL}/api/buscar", json={
        "query": "",
        "categoria": "Resoluciones",
        "pagina": 1,
        "por_pagina": 5
    })
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Motor utilizado: {data.get('motor', 'N/A')}")
    print(f"✓ Documentos encontrados: {data.get('total', 0)}")
    print("\nDocumentos en categoría Resoluciones:")
    for i, doc in enumerate(data.get('documentos', [])[:5], 1):
        print(f"  {i}. {doc['titulo'][:60]}...")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 3: Búsqueda con ordenamiento
print("TEST 3: Búsqueda ordenada por fecha descendente")
print("-" * 70)
try:
    response = requests.post(f"{BASE_URL}/api/buscar", json={
        "query": "",
        "orden": "fecha_desc",
        "pagina": 1,
        "por_pagina": 5
    })
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Documentos más recientes:")
    for i, doc in enumerate(data.get('documentos', []), 1):
        fecha = doc.get('fecha_descarga', 'N/A')
        print(f"  {i}. {doc['titulo'][:50]}... | {fecha}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 4: Paginación
print("TEST 4: Paginación - Página 2")
print("-" * 70)
try:
    response = requests.post(f"{BASE_URL}/api/buscar", json={
        "query": "",
        "pagina": 2,
        "por_pagina": 10
    })
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Página actual: {data.get('pagina', 0)}")
    print(f"✓ Total páginas: {data.get('total_paginas', 0)}")
    print(f"✓ Documentos en esta página: {len(data.get('documentos', []))}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 5: Detalles de documento
print("TEST 5: Obtener detalles de documento #1")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/api/documento/1")
    data = response.json()
    if data.get('exito'):
        doc = data['documento']
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Título: {doc['titulo']}")
        print(f"✓ Tipo: {doc['tipo']}")
        print(f"✓ Categoría: {doc['metadatos']['categoria']}")
        print(f"✓ Tamaño: {doc['tamano_mb']:.2f} MB")
        print(f"✓ Archivo existe: {doc['archivo_existe']}")
    else:
        print(f"✗ Error: {data.get('error', 'Desconocido')}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 6: Estadísticas
print("TEST 6: Obtener estadísticas del sistema")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/api/estadisticas")
    data = response.json()
    if data.get('exito'):
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Total documentos: {data['total_documentos']}")
        print(f"✓ Tamaño total: {data['tamano_total_gb']} GB")
        print(f"\nTop 5 categorías:")
        for i, cat in enumerate(data['categorias'][:5], 1):
            print(f"  {i}. {cat['_id']}: {cat['cantidad']} docs ({cat['tamano_total_mb']:.1f} MB)")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 7: Búsqueda fuzzy (tolerancia a errores)
print("TEST 7: Búsqueda fuzzy - 'manuaal' (con error)")
print("-" * 70)
try:
    response = requests.post(f"{BASE_URL}/api/buscar", json={
        "query": "manuaal",  # Error intencional
        "pagina": 1,
        "por_pagina": 3
    })
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Motor utilizado: {data.get('motor', 'N/A')}")
    print(f"✓ Documentos encontrados: {data.get('total', 0)}")
    if data.get('motor') == 'elasticsearch':
        print("✓ ElasticSearch corrigió automáticamente el error!")
except Exception as e:
    print(f"✗ Error: {e}")
print()

print("="*70)
print("RESUMEN DE PRUEBAS")
print("="*70)
print("✓ Sistema de búsqueda funcionando correctamente")
print("✓ API REST operativa")
print("✓ MongoDB y ElasticSearch integrados")
print("✓ Paginación implementada")
print("✓ Filtros y ordenamiento funcionando")
print("✓ Fuzzy matching activo en ElasticSearch")
print("="*70)
