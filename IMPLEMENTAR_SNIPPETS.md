# Implementar Extractos de Búsqueda (Snippets) con Highlighting

## 🎯 Objetivo

Mostrar fragmentos del contenido del documento donde aparece la palabra buscada, con la palabra resaltada.

**Ejemplo**:
```
Búsqueda: "justicia"

Resultado:
"...intervención del Ministerio Público en el proceso de **justicia** y paz, 
garantizando los derechos de las víctimas..."
```

---

## 📝 Implementación

### Paso 1: Crear función para generar snippets

Crea un nuevo archivo `helpers/text_utils.py`:

```python
import re
from typing import List, Dict

def generar_snippet(texto: str, query: str, max_length: int = 200) -> str:
    """
    Genera un snippet del texto mostrando el contexto donde aparece la query.
    
    Args:
        texto: Texto completo del documento
        query: Palabra o frase buscada
        max_length: Longitud máxima del snippet
        
    Returns:
        Snippet con la palabra resaltada
    """
    if not texto or not query:
        return ""
    
    # Buscar la primera ocurrencia (case insensitive)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    match = pattern.search(texto)
    
    if not match:
        # Si no encuentra, retornar inicio del texto
        return texto[:max_length] + "..." if len(texto) > max_length else texto
    
    # Posición donde aparece la palabra
    start_pos = match.start()
    end_pos = match.end()
    
    # Calcular contexto antes y después
    context_before = max_length // 2
    context_after = max_length // 2
    
    # Ajustar inicio del snippet
    snippet_start = max(0, start_pos - context_before)
    snippet_end = min(len(texto), end_pos + context_after)
    
    # Extraer snippet
    snippet = texto[snippet_start:snippet_end]
    
    # Agregar "..." si no empieza/termina en el inicio/fin del texto
    if snippet_start > 0:
        snippet = "..." + snippet
    if snippet_end < len(texto):
        snippet = snippet + "..."
    
    return snippet.strip()


def resaltar_texto(texto: str, query: str) -> str:
    """
    Resalta todas las ocurrencias de la query en el texto.
    
    Args:
        texto: Texto donde resaltar
        query: Palabra a resaltar
        
    Returns:
        Texto con marcadores de resaltado
    """
    if not texto or not query:
        return texto
    
    # Reemplazar todas las ocurrencias (case insensitive) con marcadores
    pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
    return pattern.sub(r'<mark>\1</mark>', texto)


def generar_snippets_multiples(texto: str, query: str, max_snippets: int = 3, max_length: int = 150) -> List[str]:
    """
    Genera múltiples snippets si la palabra aparece varias veces.
    
    Args:
        texto: Texto completo
        query: Palabra buscada
        max_snippets: Número máximo de snippets a generar
        max_length: Longitud de cada snippet
        
    Returns:
        Lista de snippets
    """
    if not texto or not query:
        return []
    
    snippets = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    matches = list(pattern.finditer(texto))
    
    if not matches:
        # Si no hay coincidencias, retornar inicio del texto
        return [texto[:max_length] + "..." if len(texto) > max_length else texto]
    
    # Tomar las primeras N ocurrencias
    for match in matches[:max_snippets]:
        start_pos = match.start()
        end_pos = match.end()
        
        context = max_length // 2
        snippet_start = max(0, start_pos - context)
        snippet_end = min(len(texto), end_pos + context)
        
        snippet = texto[snippet_start:snippet_end]
        
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(texto):
            snippet = snippet + "..."
        
        snippets.append(snippet.strip())
    
    return snippets
```

---

### Paso 2: Modificar la búsqueda en `helpers/mongo_db.py`

Agrega el método para generar snippets:

```python
from helpers.text_utils import generar_snippet, resaltar_texto

def buscar_documentos_con_snippets(self, query: str, categoria: str, tipo: str, skip: int, limit: int, sort_config: List[tuple]) -> tuple[List[Dict], int]:
    """Busca documentos y genera snippets del contenido."""
    try:
        # Búsqueda normal
        documentos, total = self.buscar_documentos(query, categoria, tipo, skip, limit, sort_config)
        
        # Agregar snippets si hay query
        if query:
            for doc in documentos:
                texto_contenido = doc.get('texto_contenido', '')
                if texto_contenido:
                    # Generar snippet
                    snippet = generar_snippet(texto_contenido, query, max_length=200)
                    # Resaltar la palabra buscada
                    snippet_resaltado = resaltar_texto(snippet, query)
                    doc['snippet'] = snippet_resaltado
                else:
                    doc['snippet'] = "No hay contenido de texto disponible."
        
        return documentos, total
        
    except Exception as e:
        logger.error(f"Error al buscar con snippets: {e}")
        return [], 0
```

---

### Paso 3: Actualizar la API en `app.py`

Modifica la ruta `/api/buscar`:

```python
@app.route('/api/buscar', methods=['POST'])
def api_buscar():
    """API para búsqueda de documentos con snippets"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        categoria = data.get('categoria', '')
        tipo = data.get('tipo', '')
        pagina = int(data.get('pagina', 1))
        por_pagina = int(data.get('por_pagina', 10))
        orden = data.get('orden', 'reciente')
        
        # Configurar ordenamiento
        sort_config = [('fecha_descarga', -1)] if orden == 'reciente' else [('titulo', 1)]
        
        skip = (pagina - 1) * por_pagina
        
        # Intentar con ElasticSearch primero
        if elastic_search and elastic_search.es_client:
            try:
                resultados_elastic = elastic_search.buscar_documentos(
                    query, categoria, tipo, pagina, por_pagina, orden
                )
                
                # Agregar snippets de Elasticsearch
                for doc in resultados_elastic['documentos']:
                    # Elasticsearch ya proporciona highlights
                    if 'highlight' in doc:
                        doc['snippet'] = doc['highlight'].get('texto_contenido', [''])[0]
                    else:
                        doc['snippet'] = doc.get('texto_contenido', '')[:200] + "..."
                
                return jsonify(resultados_elastic)
            except Exception as e:
                logger.warning(f"Error en ElasticSearch (fallback a Mongo): {e}")
        
        # Fallback a MongoDB con snippets
        documentos, total = mongo_db.buscar_documentos_con_snippets(
            query, categoria, tipo, skip, por_pagina, sort_config
        )
        
        total_paginas = (total + por_pagina - 1) // por_pagina
        
        resultados = {
            'documentos': documentos,
            'total': total,
            'pagina_actual': pagina,
            'total_paginas': total_paginas,
            'query': query,
            'motor': 'mongodb'
        }
        return jsonify(resultados)
        
    except Exception as e:
        logger.error(f"Error al realizar la búsqueda: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al realizar la búsqueda'
        }), 500
```

---

### Paso 4: Actualizar el Frontend en `templates/documentos.html`

Modifica la función que muestra los detalles del documento:

```javascript
function mostrarDetalles(doc) {
    const modal = document.getElementById('modalDetalles');
    const content = document.getElementById('detalleContenido');
    
    // Generar snippet o mostrar contenido completo
    let contenidoHTML = '';
    if (doc.snippet) {
        contenidoHTML = `
            <div class="alert alert-info">
                <strong>📍 Fragmento relevante:</strong>
            </div>
            <div class="snippet-container">
                ${doc.snippet}
            </div>
        `;
    } else if (doc.texto_contenido) {
        const preview = doc.texto_contenido.substring(0, 500);
        contenidoHTML = `
            <div class="text-muted">
                ${preview}${doc.texto_contenido.length > 500 ? '...' : ''}
            </div>
        `;
    } else {
        contenidoHTML = '<p class="text-muted">No hay contenido de texto disponible.</p>';
    }
    
    content.innerHTML = `
        <h4>${doc.titulo}</h4>
        <div class="row mb-3">
            <div class="col-md-6">
                <strong>Tipo:</strong> <span class="badge bg-secondary">${doc.tipo}</span>
            </div>
            <div class="col-md-6">
                <strong>Categoría:</strong> <span class="badge bg-info">${doc.metadatos?.categoria || 'N/A'}</span>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-md-6">
                <strong>Fecha Descarga:</strong> ${new Date(doc.fecha_descarga).toLocaleString()}
            </div>
            <div class="col-md-6">
                <strong>Tamaño:</strong> ${(doc.metadatos?.tamano_mb || 0).toFixed(2)} MB
            </div>
        </div>
        <div class="mb-3">
            <strong>URL Original:</strong><br>
            <a href="${doc.url_original}" target="_blank" class="text-break">${doc.url_original}</a>
        </div>
        <div class="mb-3">
            <strong>Archivo Local:</strong> ${doc.archivo_local}
        </div>
        <hr>
        <h5>Contenido:</h5>
        ${contenidoHTML}
        <div class="mt-3">
            <button class="btn btn-secondary" onclick="cerrarModal()">Cerrar</button>
        </div>
    `;
    
    modal.style.display = 'block';
}
```

---

### Paso 5: Agregar estilos CSS para el resaltado

En `templates/documentos.html`, agrega estos estilos:

```html
<style>
    /* Estilos para snippets */
    .snippet-container {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
        font-family: 'Georgia', serif;
        line-height: 1.6;
    }
    
    /* Resaltado de palabras encontradas */
    .snippet-container mark {
        background-color: #ffeb3b;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
        color: #000;
    }
    
    /* Animación para el resaltado */
    .snippet-container mark {
        animation: highlight-pulse 1.5s ease-in-out;
    }
    
    @keyframes highlight-pulse {
        0%, 100% { background-color: #ffeb3b; }
        50% { background-color: #ffd700; }
    }
</style>
```

---

## 🎨 Resultado Final

Cuando busques "justicia", verás algo como:

```
📍 Fragmento relevante:

...intervención del Ministerio Público en el proceso de justicia y paz, 
garantizando los derechos de las víctimas y la reparación integral...
```

Con la palabra "justicia" resaltada en amarillo.

---

## 🚀 Implementación Rápida

Si quieres una versión más simple sin crear archivos nuevos, puedes agregar esta función directamente en `app.py`:

```python
def generar_snippet_simple(texto, query, max_length=200):
    """Genera snippet simple del texto"""
    if not texto or not query:
        return "No hay contenido disponible."
    
    # Buscar la palabra (case insensitive)
    texto_lower = texto.lower()
    query_lower = query.lower()
    pos = texto_lower.find(query_lower)
    
    if pos == -1:
        # Si no encuentra, retornar inicio
        return texto[:max_length] + "..."
    
    # Extraer contexto
    start = max(0, pos - 100)
    end = min(len(texto), pos + len(query) + 100)
    snippet = texto[start:end]
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(texto):
        snippet = snippet + "..."
    
    # Resaltar la palabra
    snippet = snippet.replace(query, f"<mark>{query}</mark>")
    snippet = snippet.replace(query.upper(), f"<mark>{query.upper()}</mark>")
    snippet = snippet.replace(query.capitalize(), f"<mark>{query.capitalize()}</mark>")
    
    return snippet
```

---

¿Quieres que implemente esta funcionalidad completa o prefieres la versión simple?
