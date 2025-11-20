# Documentación de la API

## Índice

- [Introducción](#introducción)
- [Autenticación](#autenticación)
- [Endpoints](#endpoints)
- [Modelos de Datos](#modelos-de-datos)
- [Códigos de Error](#códigos-de-error)

## Introducción

La API del Proyecto Big Data proporciona acceso programático a la búsqueda de documentos jurídicos de la Procuraduría General de la Nación de Colombia.

**Base URL**: `http://localhost:5001` (desarrollo) o `https://tu-app.onrender.com` (producción)

## Autenticación

### Login

Inicia sesión y obtiene una sesión activa.

**Endpoint**: `POST /login`

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta Exitosa** (200):
```json
{
  "exito": true,
  "mensaje": "Login exitoso",
  "usuario": "admin"
}
```

**Respuesta Error** (401):
```json
{
  "exito": false,
  "mensaje": "Usuario o contraseña incorrectos"
}
```

### Logout

Cierra la sesión activa.

**Endpoint**: `GET /logout`

**Respuesta** (302):
Redirección a la página de login.

## Endpoints

### 1. Búsqueda de Documentos

Busca documentos por término, categoría y tipo.

**Endpoint**: `POST /api/buscar`

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "query": "código de ética",
  "categoria": "Códigos y Normatividad",
  "tipo": "PDF",
  "pagina": 1,
  "limite": 10,
  "ordenar_por": "relevancia"
}
```

**Parámetros**:

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| query | string | Sí | Término de búsqueda |
| categoria | string | No | Filtrar por categoría específica |
| tipo | string | No | Filtrar por tipo de archivo (PDF, Excel, Word) |
| pagina | integer | No | Número de página (default: 1) |
| limite | integer | No | Resultados por página (default: 10) |
| ordenar_por | string | No | Criterio de orden: relevancia, fecha_desc, fecha_asc, nombre_asc, nombre_desc |

**Respuesta Exitosa** (200):
```json
{
  "exito": true,
  "resultados": [
    {
      "numero": "DOC001",
      "titulo": "Código de Ética",
      "categoria": "Códigos y Normatividad",
      "tipo": "PDF",
      "url": "https://ejemplo.com/doc.pdf",
      "tamano": "1.5 MB",
      "fecha": "2024-01-15",
      "descripcion": "Código de ética de la entidad"
    }
  ],
  "total": 5,
  "pagina_actual": 1,
  "total_paginas": 1,
  "limite": 10,
  "mensaje": "Búsqueda realizada con éxito"
}
```

**Respuesta Sin Resultados** (200):
```json
{
  "exito": true,
  "resultados": [],
  "total": 0,
  "mensaje": "No se encontraron resultados"
}
```

**Respuesta Error** (500):
```json
{
  "exito": false,
  "mensaje": "Error al realizar la búsqueda",
  "error": "Descripción técnica del error"
}
```

### 2. Obtener Documento por ID

Obtiene los detalles completos de un documento específico.

**Endpoint**: `GET /api/documento/<numero>`

**Parámetros de URL**:

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| numero | string | Número de documento único |

**Ejemplo**: `/api/documento/DOC001`

**Respuesta Exitosa** (200):
```json
{
  "exito": true,
  "documento": {
    "numero": "DOC001",
    "titulo": "Código de Ética",
    "categoria": "Códigos y Normatividad",
    "tipo": "PDF",
    "url": "https://ejemplo.com/doc.pdf",
    "tamano": "1.5 MB",
    "fecha": "2024-01-15",
    "descripcion": "Código de ética de la entidad",
    "metadata": {
      "paginas": 50,
      "idioma": "Español",
      "autor": "Procuraduría General"
    }
  }
}
```

**Respuesta No Encontrado** (404):
```json
{
  "exito": false,
  "mensaje": "Documento no encontrado"
}
```

### 3. Obtener Estadísticas

Obtiene estadísticas generales del sistema.

**Endpoint**: `GET /api/estadisticas`

**Headers**:
```http
Cookie: session=<session_cookie>
```

**Respuesta Exitosa** (200):
```json
{
  "exito": true,
  "estadisticas": {
    "total_documentos": 98,
    "categorias": [
      {
        "nombre": "Otros Documentos",
        "cantidad": 68
      },
      {
        "nombre": "Resoluciones",
        "cantidad": 12
      }
    ],
    "tipos": [
      {
        "nombre": "PDF",
        "cantidad": 85
      },
      {
        "nombre": "Excel",
        "cantidad": 13
      }
    ],
    "tamano_total": "527 MB"
  }
}
```

**Respuesta No Autorizado** (401):
```json
{
  "exito": false,
  "mensaje": "Acceso no autorizado"
}
```

## Modelos de Datos

### Documento

```typescript
interface Documento {
  numero: string;           // ID único del documento
  titulo: string;           // Título descriptivo
  categoria: string;        // Categoría del documento
  tipo: string;             // Tipo de archivo: PDF, Excel, Word
  url: string;              // URL de descarga
  tamano: string;           // Tamaño del archivo (ej: "1.5 MB")
  fecha: string;            // Fecha de publicación (YYYY-MM-DD)
  descripcion: string;      // Descripción breve
  metadata?: {              // Metadatos adicionales (opcional)
    paginas?: number;
    idioma?: string;
    autor?: string;
  }
}
```

### Categorías Disponibles

- Códigos y Normatividad
- Informes de Gestión
- Manuales y Procedimientos
- Resoluciones
- Otros Documentos

### Tipos de Archivo

- PDF
- Excel
- Word

### Opciones de Ordenamiento

- `relevancia`: Orden por relevancia de búsqueda (default)
- `fecha_desc`: Fecha descendente (más reciente primero)
- `fecha_asc`: Fecha ascendente (más antiguo primero)
- `nombre_asc`: Nombre alfabético A-Z
- `nombre_desc`: Nombre alfabético Z-A

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | Solicitud exitosa |
| 400 | Solicitud inválida - parámetros incorrectos |
| 401 | No autorizado - requiere autenticación |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |
| 503 | Servicio no disponible - base de datos inaccesible |

## Ejemplos de Uso

### Python

```python
import requests

# Login
login_url = "http://localhost:5001/login"
login_data = {
    "username": "admin",
    "password": "admin123"
}
session = requests.Session()
response = session.post(login_url, json=login_data)

# Búsqueda
search_url = "http://localhost:5001/api/buscar"
search_data = {
    "query": "resolución",
    "categoria": "Resoluciones",
    "pagina": 1,
    "limite": 10
}
response = session.post(search_url, json=search_data)
resultados = response.json()

# Obtener documento específico
doc_url = "http://localhost:5001/api/documento/DOC001"
response = session.get(doc_url)
documento = response.json()
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:5001/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  }),
  credentials: 'include'
});

// Búsqueda
const searchResponse = await fetch('http://localhost:5001/api/buscar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'código',
    categoria: 'Códigos y Normatividad',
    pagina: 1
  }),
  credentials: 'include'
});
const data = await searchResponse.json();
```

### cURL

```bash
# Login
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# Búsqueda
curl -X POST http://localhost:5001/api/buscar \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "query": "manual",
    "categoria": "Manuales y Procedimientos"
  }'
```

## Límites y Consideraciones

- **Rate Limiting**: No hay límite de solicitudes actualmente
- **Tamaño de Respuesta**: Máximo 100 resultados por página
- **Timeout**: 30 segundos por solicitud
- **Caché**: ElasticSearch cachea automáticamente búsquedas frecuentes

## Versionado

Versión actual: **v1**

La API sigue Semantic Versioning. Cambios breaking incluirán un incremento de versión mayor.

---

**Última actualización**: Noviembre 2025
