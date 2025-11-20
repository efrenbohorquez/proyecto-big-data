# Sistema de Búsqueda de Documentos
## Proyecto Big Data - Universidad Central

### Autor
Efren Bohorquez Vargas

### Fecha
19 de Noviembre de 2025

---

## 🚀 Características Principales

### 1. **Arquitectura Híbrida MongoDB + ElasticSearch**
- **MongoDB**: Base de datos principal para almacenamiento estructurado
- **ElasticSearch**: Motor de búsqueda avanzado para queries de texto completo
- **Fallback automático**: Si ElasticSearch falla, usa MongoDB como respaldo

### 2. **Búsqueda Inteligente**
- ✅ Búsqueda de texto completo con tolerancia a errores (fuzzy matching)
- ✅ Múltiples campos de búsqueda: título, tipo, categoría
- ✅ Búsqueda ponderada: títulos tienen 3x más relevancia
- ✅ Highlights en resultados (resalta términos encontrados)
- ✅ Scoring de relevancia automático

### 3. **Filtros Avanzados**
- Filtro por categoría (6 categorías disponibles)
- Filtro por tipo de documento (PDF, DOCX, DOC)
- Ordenamiento múltiple:
  - Por relevancia (scoring de ElasticSearch)
  - Por fecha descendente (más recientes primero)
  - Por fecha ascendente (más antiguos primero)
  - Por título alfabético

### 4. **Paginación Eficiente**
- Navegación por páginas (10 documentos por página)
- Botones de primera/última página
- Botones anterior/siguiente
- Indicador visual de página actual
- URLs limpias sin recarga de página

### 5. **API REST JSON**
Endpoints disponibles:

#### `POST /api/buscar`
Búsqueda de documentos con filtros y paginación.

**Request:**
```json
{
  "query": "manual",
  "categoria": "Manuales y Procedimientos",
  "tipo": "PDF",
  "orden": "relevancia",
  "pagina": 1,
  "por_pagina": 10
}
```

**Response:**
```json
{
  "exito": true,
  "documentos": [...],
  "total": 98,
  "pagina": 1,
  "por_pagina": 10,
  "total_paginas": 10,
  "query": "manual",
  "motor": "elasticsearch"
}
```

#### `GET /api/documento/<numero>`
Obtener detalles completos de un documento específico.

**Response:**
```json
{
  "exito": true,
  "documento": {
    "numero": 1,
    "titulo": "Manual de Funciones",
    "tipo": "PDF",
    "tamano_mb": 14.5,
    "url_original": "...",
    "archivo_local": "...",
    ...
  }
}
```

#### `GET /api/estadisticas`
Obtener estadísticas agregadas del sistema.

**Response:**
```json
{
  "exito": true,
  "total_documentos": 98,
  "tamano_total_gb": 0.52,
  "categorias": [...],
  "tipos": [...],
  "años": [...]
}
```

---

## 🎨 Interfaz de Usuario (Frontend)

### Tecnologías Utilizadas
1. **Vue.js 3** - Framework JavaScript progresivo
2. **Bootstrap 5** - Framework CSS responsivo
3. **Font Awesome 6** - Iconos profesionales
4. **Axios** - Cliente HTTP para APIs

### Características de la UI

#### 1. Dashboard de Estadísticas
- Total de documentos en el sistema
- Número de categorías disponibles
- Tipos de archivos indexados
- Almacenamiento total en GB

#### 2. Barra de Búsqueda
- Input con autocompletado
- Búsqueda en tiempo real (Enter o botón)
- Placeholder con ejemplos de uso
- Icono de búsqueda animado

#### 3. Sección de Filtros
- Selectores dropdown para categoría y tipo
- Contador de documentos por categoría
- Selector de ordenamiento
- Botón de limpiar filtros

#### 4. Tarjetas de Documentos
- Diseño moderno con hover effects
- Iconos según tipo de archivo
- Badges de categoría con colores distintos
- Metadatos: tamaño, año, tipo, scoring
- Botones de acción: ver detalles y descargar

#### 5. Sistema de Paginación
- Navegación completa (primera, anterior, páginas visibles, siguiente, última)
- Indicador visual de página activa
- Deshabilitación inteligente de botones
- Scroll automático al cambiar página

#### 6. Modal de Detalles
- Información completa del documento
- URL original con enlace
- Estado de disponibilidad
- Botón de descarga directa

#### 7. Estados de la UI
- **Loading**: Spinner animado durante búsquedas
- **Resultados**: Lista de documentos con paginación
- **Sin resultados**: Mensaje amigable con sugerencias
- **Error**: Manejo de errores con alertas

---

## 🔧 Implementación Técnica

### Backend (Flask + Python)

#### Estructura de Rutas

```python
# Páginas
GET  /                  → Landing page
GET  /documentos        → Interfaz de búsqueda

# API REST
POST /api/buscar        → Búsqueda con filtros
GET  /api/documento/<n> → Detalles de documento
GET  /api/estadisticas  → Estadísticas generales
```

#### Funciones Clave

**1. `buscar_con_elasticsearch(query, categoria, tipo, pagina, por_pagina, orden)`**
- Construye query DSL de ElasticSearch
- Implementa búsqueda fuzzy (tolerancia a errores)
- Multi-match en múltiples campos
- Filtros con términos exactos
- Ordenamiento configurable
- Highlights de resultados

**2. `buscar_con_mongodb(query, categoria, tipo, pagina, por_pagina, orden)`**
- Búsqueda con regex (case-insensitive)
- OR logic entre múltiples campos
- Filtros con match exacto
- Sorting por múltiples campos
- Skip/Limit para paginación

**3. `api_buscar_documentos()`**
- Validación de parámetros
- Límites de seguridad (1-100 por página)
- Try-catch con fallback automático
- Respuesta JSON estandarizada

### Frontend (Vue.js 3)

#### Estructura del Componente

```javascript
data() {
  return {
    // Búsqueda
    query: '',
    categoria: '',
    tipo: '',
    orden: 'relevancia',
    
    // Paginación
    paginaActual: 1,
    porPagina: 10,
    
    // Resultados
    resultados: {},
    motor: '',
    loading: false
  }
}
```

#### Métodos Principales

**1. `buscar()`**
- Reset a página 1
- POST a `/api/buscar`
- Actualiza resultados y motor
- Manejo de errores

**2. `cambiarPagina(pagina)`**
- Validación de página
- POST con nueva página
- Scroll to top
- Loading state

**3. `verDetalle(numero)`**
- GET a `/api/documento/<numero>`
- Abre modal de Bootstrap
- Muestra información completa

**4. `limpiarFiltros()`**
- Reset de todos los filtros
- Limpia query
- Reinicia resultados

---

## 📊 Queries de ElasticSearch

### Query DSL Generada

```json
{
  "bool": {
    "must": [
      {
        "multi_match": {
          "query": "manual",
          "fields": ["titulo^3", "tipo^2", "metadatos.categoria"],
          "fuzziness": "AUTO",
          "operator": "or"
        }
      }
    ],
    "filter": [
      { "term": { "metadatos.categoria": "Manuales y Procedimientos" } },
      { "term": { "tipo.keyword": "PDF" } }
    ]
  }
}
```

### Configuración de Highlights

```json
{
  "highlight": {
    "fields": {
      "titulo": {},
      "tipo": {}
    }
  }
}
```

### Opciones de Ordenamiento

```python
# Por relevancia (default)
sort_config = ['_score']

# Por fecha descendente
sort_config = [{'fecha_descarga': {'order': 'desc'}}]

# Por título alfabético
sort_config = [{'titulo.keyword': {'order': 'asc'}}]
```

---

## 🎯 Casos de Uso

### 1. Búsqueda Simple
**Usuario busca:** "manual"
**Sistema hace:**
- ElasticSearch busca en título (x3), tipo (x2), categoría
- Fuzzy matching tolera errores de escritura
- Retorna 6 documentos ordenados por relevancia
- Muestra scoring de cada resultado

### 2. Búsqueda con Filtros
**Usuario busca:** "resolución" + categoría="Resoluciones" + tipo="PDF"
**Sistema hace:**
- Query de texto en ElasticSearch
- Filtros exactos por categoría y tipo
- Solo retorna PDFs en categoría Resoluciones
- Paginación de resultados

### 3. Exploración por Categoría
**Usuario selecciona:** categoría="Códigos y Normatividad"
**Sistema hace:**
- Query sin texto (match_all)
- Filtro por categoría
- Retorna 4 documentos de esa categoría
- Ordenados por fecha descendente

### 4. Fallback Automático
**Escenario:** ElasticSearch no disponible
**Sistema hace:**
- Detecta error en ElasticSearch
- Automáticamente usa MongoDB
- Búsqueda con regex en MongoDB
- Usuario no nota diferencia
- Badge indica "mongodb" como motor

---

## 🔍 Optimizaciones Implementadas

### 1. Performance
- Índices en MongoDB (titulo, tipo, categoria, fecha_descarga)
- Paginación server-side (reduce transferencia)
- Límite de 100 resultados por página
- Lazy loading de detalles (solo al hacer click)

### 2. Experiencia de Usuario
- Loading states durante búsquedas
- Scroll automático al cambiar página
- Highlights en resultados de ElasticSearch
- Colores distintos por categoría
- Iconos según tipo de archivo

### 3. Seguridad
- Validación de parámetros en backend
- Límites en por_pagina (1-100)
- Sanitización de ObjectId
- Try-catch en todas las operaciones
- Manejo de errores sin exponer detalles

### 4. Escalabilidad
- API REST stateless
- Paginación eficiente
- Caché automático de ElasticSearch
- Índices optimizados en MongoDB

---

## 📈 Métricas del Sistema

### Datos Actuales
- **Total documentos**: 98
- **Categorías**: 6
- **Tipos**: 3 (PDF, DOCX, DOC)
- **Almacenamiento**: 527.36 MB
- **Índice ElasticSearch**: procuraduria_documentos
- **Colección MongoDB**: documentos_procuraduria

### Distribución por Categoría
1. Otros Documentos: 68 (69.4%)
2. Resoluciones: 12 (12.2%)
3. Manuales y Procedimientos: 7 (7.1%)
4. Códigos y Normatividad: 4 (4.1%)
5. Informes de Gestión: 4 (4.1%)
6. Guías y Protocolos: 3 (3.1%)

---

## 🚀 Próximas Mejoras

### Fase 1: Búsqueda Avanzada
- [ ] Filtros por rango de fechas
- [ ] Filtro por tamaño de archivo
- [ ] Búsqueda en contenido de PDFs (OCR)
- [ ] Sugerencias de búsqueda (autocomplete)
- [ ] Búsquedas guardadas

### Fase 2: Análisis
- [ ] Dashboard de analytics
- [ ] Gráficos con Chart.js
- [ ] Trending searches
- [ ] Documentos más descargados
- [ ] Reportes en Excel/PDF

### Fase 3: Social
- [ ] Sistema de favoritos
- [ ] Compartir documentos
- [ ] Comentarios y ratings
- [ ] Tags personalizados
- [ ] Historial de búsquedas

---

## 📚 Referencias

### Tecnologías
- Flask 3.1.2: https://flask.palletsprojects.com/
- MongoDB Atlas: https://www.mongodb.com/atlas
- ElasticSearch 8.11: https://www.elastic.co/elasticsearch/
- Vue.js 3: https://vuejs.org/
- Bootstrap 5: https://getbootstrap.com/

### Patrones de Diseño
- REST API Best Practices
- Repository Pattern (MongoDB/ElasticSearch)
- MVVM con Vue.js
- Progressive Enhancement
- Mobile-First Responsive Design

---

## ✅ Conclusión

El sistema de búsqueda implementado combina lo mejor de dos mundos:
- **MongoDB** para almacenamiento confiable y consultas estructuradas
- **ElasticSearch** para búsquedas de texto completo y análisis avanzado

Con una interfaz moderna en **Vue.js 3** y **Bootstrap 5**, proporciona una experiencia de usuario fluida y profesional, siguiendo las últimas tendencias de desarrollo web.

**Versión**: 1.1  
**Autor**: Efren Bohorquez Vargas  
**Institución**: Universidad Central - Maestría en Analítica  
**Fecha**: 19 de Noviembre de 2025
