# Arquitectura del Sistema

## Índice

- [Visión General](#visión-general)
- [Componentes](#componentes)
- [Flujo de Datos](#flujo-de-datos)
- [Tecnologías](#tecnologías)
- [Patrones de Diseño](#patrones-de-diseño)

## Visión General

El Proyecto Big Data es una aplicación web para búsqueda y gestión de documentos jurídicos, implementada con arquitectura de tres capas y servicios en la nube.

```
┌─────────────────────────────────────────────────┐
│              Frontend (Capa de Presentación)     │
│  Bootstrap 5 + JavaScript ES6 + HTML5 Templates │
└────────────────┬────────────────────────────────┘
                 │ HTTP/HTTPS
┌────────────────▼────────────────────────────────┐
│         Backend (Capa de Aplicación)            │
│  Flask 3.0 + Python 3.11 + Gunicorn            │
└─────┬──────────────────────────────┬───────────┘
      │                              │
      │ MongoDB Driver              │ ES Client
      │                              │
┌─────▼─────────────┐      ┌─────────▼──────────┐
│  MongoDB Atlas    │      │  ElasticSearch     │
│  (Base de Datos)  │      │  (Motor de Búsq.)  │
└───────────────────┘      └────────────────────┘
```

## Componentes

### 1. Frontend (Client-Side)

**Ubicación**: `/templates`

**Archivos principales**:
- `landing.html`: Página de inicio
- `login.html`: Autenticación
- `documentos.html`: Búsqueda de documentos
- `admin.html`: Panel de administración
- `about.html`: Información del proyecto

**Responsabilidades**:
- Renderizado de interfaces de usuario
- Validación de formularios client-side
- Llamadas AJAX a la API REST
- Manejo de eventos y navegación

**Tecnologías**:
- Bootstrap 5.3 (CSS Framework)
- Font Awesome 6.4 (Iconos)
- JavaScript ES6+ (Lógica del cliente)
- Fetch API (Comunicación HTTP)

### 2. Backend (Server-Side)

**Ubicación**: `/app.py`, `/helpers`

#### 2.1 Aplicación Principal (`app.py`)

**Responsabilidades**:
- Manejo de rutas HTTP
- Gestión de sesiones
- Autenticación y autorización
- Orquestación de servicios
- Manejo de errores

**Endpoints principales**:
```python
GET  /                  # Landing page
GET  /login            # Página de login
POST /login            # Autenticación
GET  /logout           # Cerrar sesión
GET  /documentos       # Búsqueda UI
GET  /admin            # Panel admin
POST /api/buscar       # API búsqueda
GET  /api/documento/<id> # Detalle documento
```

#### 2.2 Módulo MongoDB (`helpers/mongo_db.py`)

**Clase**: `Mongo_DB`

**Responsabilidades**:
- Conexión con MongoDB Atlas
- Operaciones CRUD
- Consultas de agregación
- Generación de estadísticas

**Métodos principales**:
```python
conectar() -> bool
buscar_documentos(query, filtros) -> List[Dict]
buscar_usuario(username) -> Dict | None
obtener_estadisticas() -> Dict
agregar_documento(documento) -> str
```

#### 2.3 Módulo ElasticSearch (`helpers/elasticsearch.py`)

**Clase**: `ElasticSearch`

**Responsabilidades**:
- Conexión con ElasticSearch Cloud
- Búsqueda full-text avanzada
- Indexación de documentos
- Búsqueda difusa (fuzzy search)

**Métodos principales**:
```python
conectar() -> bool
buscar_documentos(query, filtros) -> List[Dict]
indexar_documento(documento) -> bool
obtener_sugerencias(termino) -> List[str]
```

#### 2.4 Módulo de Funciones (`helpers/funciones.py`)

**Responsabilidades**:
- Utilidades generales
- Formateo de datos
- Validaciones
- Conversiones

**Funciones principales**:
```python
formatear_fecha(fecha_str) -> str
validar_email(email) -> bool
calcular_tamano_archivo(bytes) -> str
sanitizar_input(texto) -> str
```

#### 2.5 Web Scraper (`helpers/web_scraper.py`)

**Responsabilidades**:
- Extracción de documentos
- Parsing de HTML
- Descarga de archivos
- Generación de reportes

**Funciones principales**:
```python
extraer_documentos(url) -> List[Dict]
descargar_pdf(url, ruta) -> bool
generar_reporte(documentos) -> str
```

### 3. Capa de Datos

#### 3.1 MongoDB Atlas

**Tipo**: Base de datos NoSQL (Document Store)

**Bases de datos**:
- `proyecto_big_data`

**Colecciones**:
- `documentos_procuraduria` (98 documentos)
- `usuarios` (usuarios del sistema)
- `sesiones` (gestión de sesiones)

**Esquema de documento**:
```json
{
  "_id": ObjectId,
  "numero": "DOC001",
  "titulo": "Código de Ética",
  "categoria": "Códigos y Normatividad",
  "tipo": "PDF",
  "url": "https://...",
  "tamano": "1.5 MB",
  "fecha": "2024-01-15",
  "descripcion": "...",
  "metadata": {
    "paginas": 50,
    "idioma": "Español"
  }
}
```

**Índices**:
- `numero`: Único
- `categoria`: Compuesto
- `titulo`: Texto completo

#### 3.2 ElasticSearch Cloud

**Tipo**: Motor de búsqueda full-text

**Índices**:
- `documentos_procuraduria`

**Mapeo de campos**:
```json
{
  "mappings": {
    "properties": {
      "titulo": { "type": "text", "analyzer": "spanish" },
      "descripcion": { "type": "text", "analyzer": "spanish" },
      "categoria": { "type": "keyword" },
      "tipo": { "type": "keyword" },
      "fecha": { "type": "date" },
      "numero": { "type": "keyword" }
    }
  }
}
```

**Capacidades**:
- Búsqueda fuzzy (tolerancia a errores)
- Scoring de relevancia
- Faceted search
- Agregaciones

## Flujo de Datos

### 1. Flujo de Búsqueda

```
Usuario ingresa término
        │
        ▼
Frontend valida input
        │
        ▼
POST /api/buscar
        │
        ▼
Backend recibe request
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
Intenta ElasticSearch    ¿ElasticSearch falla?
        │                      │
        │                      │ Sí
        │                      ▼
        │              Fallback a MongoDB
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
        Ordena y pagina resultados
                   │
                   ▼
        Devuelve JSON response
                   │
                   ▼
        Frontend renderiza resultados
```

### 2. Flujo de Autenticación

```
Usuario ingresa credenciales
        │
        ▼
POST /login
        │
        ▼
Backend valida formato
        │
        ▼
Consulta usuario en MongoDB
        │
        ├─────────────────┐
        │                 │
Usuario existe       Usuario no existe
        │                 │
        ▼                 ▼
Verifica contraseña  Error 401
con bcrypt                │
        │                 │
        ├─────────────────┘
        │
Hash coincide?
        │
        ├─────────────────┐
       Sí                No
        │                 │
        ▼                 ▼
Crea sesión Flask    Error 401
        │
        ▼
Redirige a /documentos
```

### 3. Flujo de Web Scraping

```
Script scraper_procuraduria.py
        │
        ▼
Conecta a página objetivo
        │
        ▼
Extrae enlaces de documentos
        │
        ▼
Para cada documento:
  │
  ├─ Extrae metadata
  ├─ Descarga archivo
  └─ Almacena en MongoDB
        │
        ▼
Genera reporte JSON
        │
        ▼
Indexa en ElasticSearch
```

## Tecnologías

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.11 | Lenguaje principal |
| Flask | 3.0.0 | Framework web |
| pymongo | 4.6.0 | Driver MongoDB |
| elasticsearch | 8.11.0 | Cliente ES |
| bcrypt | 4.0.1 | Hash contraseñas |
| Gunicorn | 21.2.0 | WSGI server |
| Requests | 2.31.0 | HTTP client |
| BeautifulSoup4 | 4.12.2 | HTML parsing |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Bootstrap | 5.3 | CSS framework |
| Font Awesome | 6.4 | Iconos |
| JavaScript | ES6+ | Lógica cliente |
| HTML5 | - | Estructura |
| CSS3 | - | Estilos |

### Infraestructura

| Servicio | Proveedor | Propósito |
|----------|-----------|-----------|
| MongoDB Atlas | MongoDB Inc. | Base de datos |
| ElasticSearch | Elastic Cloud | Motor búsqueda |
| Render | Render Inc. | Hosting web |
| GitHub | GitHub Inc. | Control versiones |

## Patrones de Diseño

### 1. MVC (Model-View-Controller)

```
Model       → helpers/mongo_db.py, helpers/elasticsearch.py
View        → templates/*.html
Controller  → app.py
```

### 2. Singleton

**Uso**: Conexiones de base de datos

```python
class Mongo_DB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 3. Facade

**Uso**: Clase `Funciones` simplifica operaciones complejas

```python
class Funciones:
    @staticmethod
    def buscar_documentos_fallback(query):
        # Simplifica lógica de fallback ES → MongoDB
        pass
```

### 4. Strategy

**Uso**: Diferentes estrategias de búsqueda

```python
def buscar(query, estrategia="elasticsearch"):
    if estrategia == "elasticsearch":
        return elastic.buscar(query)
    elif estrategia == "mongodb":
        return mongo.buscar(query)
```

### 5. Repository

**Uso**: Abstracción de acceso a datos

```python
class DocumentoRepository:
    def __init__(self, db_client):
        self.db = db_client
    
    def find_by_id(self, doc_id):
        pass
    
    def find_all(self, filters):
        pass
```

## Seguridad

### 1. Autenticación

- Contraseñas hasheadas con bcrypt (cost factor: 12)
- Sesiones Flask con cookies seguras
- Logout invalida sesión

### 2. Validación

- Sanitización de inputs
- Validación de tipos
- Límites de longitud

### 3. Configuración

- Variables de entorno para credenciales
- `.gitignore` protege `.env`
- No hardcoding de secrets

### 4. HTTPS

- Render proporciona SSL automático
- Redirect HTTP → HTTPS en producción

## Escalabilidad

### Horizontal

- Render permite múltiples instancias
- MongoDB Atlas soporta sharding
- ElasticSearch distribuido por diseño

### Vertical

- Upgrades de plan en Render
- Tiers de MongoDB Atlas
- Más nodos en ES cluster

### Caché

- ElasticSearch cachea búsquedas frecuentes
- Browser cache para assets estáticos
- Considerar Redis para sesiones

## Monitoreo

### Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logs de eventos importantes
logger.info("Usuario autenticado: admin")
logger.error("Fallo conexión MongoDB")
```

### Métricas

- Render Dashboard: CPU, memoria, requests
- MongoDB Atlas Metrics: operaciones, latencia
- ElasticSearch Monitoring: índices, consultas

## Diagramas

### Diagrama de Componentes

```
┌──────────────────────────────────────────┐
│              app.py (Flask)              │
│  ┌────────┐  ┌────────┐  ┌──────────┐   │
│  │Routes  │  │Auth    │  │Sessions  │   │
│  └────┬───┘  └───┬────┘  └────┬─────┘   │
└───────┼──────────┼────────────┼─────────┘
        │          │            │
        ▼          ▼            ▼
┌──────────────────────────────────────────┐
│              helpers/                     │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │Mongo_DB  │  │ES        │  │Funcs   │ │
│  └──────────┘  └──────────┘  └────────┘ │
└──────────────────────────────────────────┘
        │               │
        ▼               ▼
┌─────────────┐  ┌─────────────┐
│MongoDB Atlas│  │ElasticSearch│
└─────────────┘  └─────────────┘
```

### Diagrama de Secuencia (Búsqueda)

```
Usuario  Frontend  Backend  ES      MongoDB
  │        │         │       │         │
  ├───────►│ input   │       │         │
  │        ├────────►│ POST  │         │
  │        │         ├──────►│ search  │
  │        │         │       ├─X error │
  │        │         ├───────┼────────►│ find
  │        │         │       │         ├─────┐
  │        │         │◄──────┼─────────┤ docs│
  │        │◄────────┤ JSON  │         │
  │◄───────┤ render  │       │         │
```

---

**Última actualización**: Noviembre 2025
