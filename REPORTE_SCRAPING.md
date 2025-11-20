# Reporte de Web Scraping - Procuraduría General de la Nación

**Proyecto Big Data - Universidad Central**  
**Autor:** Efren Bohorquez Vargas  
**Fecha:** 19 de noviembre de 2025

---

## Resumen Ejecutivo

Se realizó un proceso de **web scraping ético** al sitio web oficial de la Procuraduría General de la Nación de Colombia, respetando las políticas de robots.txt y aplicando rate limiting de 3 segundos entre requests.

### Configuración del Scraping

- **URL Base:** https://www.procuraduria.gov.co
- **Páginas Analizadas:** 10
- **Delay entre requests:** 3.0 segundos
- **User-Agent:** Universidad Central - Proyecto Big Data (Investigación Académica)
- **Verificación robots.txt:** ✓ Permitido

---

## Resultados Obtenidos

### Estadísticas Generales

| Métrica | Cantidad |
|---------|----------|
| Páginas analizadas | 10 |
| Textos extraídos | 66 secciones |
| Enlaces encontrados | 330 |
| Tablas encontradas | 12 |
| Documentos descargables | 0 (en páginas analizadas) |

### Páginas Procesadas

1. **Página Principal**
   - URL: https://www.procuraduria.gov.co
   - Textos: 14 | Enlaces: 33 | Tablas: 0

2. **Redes Sociales**
   - URL: /Lists/RedesSociales/AllItems.aspx
   - Textos: 1 | Enlaces: 34 | Tablas: 2

3. **Audios**
   - URL: /Pages/Audios.aspx
   - Textos: 5 | Enlaces: 30 | Tablas: 0

4. **Documentos**
   - URL: /Prueba de documentos/Forms/AllItems.aspx
   - Textos: 1 | Enlaces: 29 | Tablas: 4

5. **Servicios o Enlaces**
   - URL: /Lists/Servicios o Enlaces/AllItems.aspx
   - Textos: 1 | Enlaces: 43 | Tablas: 2

6. **Parámetros**
   - URL: /Lists/Parametros/AllItems.aspx
   - Textos: 1 | Enlaces: 29 | Tablas: 2

7. **Funciones**
   - URL: /Lists/Funciones/AllItems.aspx
   - Textos: 1 | Enlaces: 34 | Tablas: 2

---

## Archivos Generados

### Reportes JSON

1. **procuraduria_scraping_20251119_110424.json** (1,508 bytes)
   - Scraping básico de página principal
   - 1 sección analizada

2. **procuraduria_scraping_avanzado_20251119_112448.json** (5,424 bytes)
   - Scraping avanzado con exploración recursiva
   - 10 páginas analizadas
   - Estadísticas completas

### Ubicación

Todos los archivos se encuentran en la carpeta: `uploads/`

---

## Metodología Aplicada

### Prácticas Éticas Implementadas

✓ **Verificación de robots.txt** - Se respetan las políticas del sitio  
✓ **Rate Limiting** - 3 segundos entre requests para no sobrecargar el servidor  
✓ **User-Agent identificable** - Se identifica como investigación académica  
✓ **Reintentos limitados** - Máximo 3 reintentos por request fallido  
✓ **Gestión de sesión** - Cierre apropiado de conexiones HTTP  

### Tecnologías Utilizadas

- **Python 3.12.4**
- **BeautifulSoup 4.14.2** - Parsing HTML
- **Requests** - HTTP client
- **lxml 6.0.2** - Parser XML/HTML
- **urllib3** - HTTP connection pooling

### Módulos Desarrollados

1. **helpers/web_scraper.py** - Módulo principal de scraping
   - Clase `WebScraper` con rate limiting
   - Verificación de robots.txt
   - Extracción de textos, enlaces y tablas
   - Descarga de archivos
   - Exportación a JSON

2. **scraper_procuraduria.py** - Script básico
3. **scraper_procuraduria_avanzado.py** - Script con exploración recursiva

---

## Capacidades del Sistema

El módulo de web scraping desarrollado permite:

- ✓ Verificar robots.txt antes de scrapear
- ✓ Extraer textos de cualquier selector CSS
- ✓ Extraer todos los enlaces de una página
- ✓ Extraer tablas HTML a formato Python
- ✓ Descargar archivos (PDF, DOCX, XLSX, ZIP)
- ✓ Scrapear múltiples páginas con rate limiting
- ✓ Exportar datos a JSON
- ✓ Exploración recursiva de sitios web
- ✓ Manejo de errores HTTP con reintentos

---

## Próximos Pasos

1. **Procesamiento de datos** - Analizar los textos extraídos
2. **Almacenamiento** - Guardar en MongoDB para consultas
3. **Indexación** - Subir a ElasticSearch para búsquedas
4. **Visualización** - Crear dashboard con estadísticas
5. **Automatización** - Programar scraping periódico

---

## Consideraciones Legales

Este scraping se realizó con fines **exclusivamente académicos** como parte del Proyecto Big Data de la Universidad Central. 

- ✓ Se respetó robots.txt
- ✓ No se sobrecargó el servidor (rate limiting)
- ✓ Se accedió solo a información pública
- ✓ Se identificó el User-Agent como investigación académica
- ✓ No se violaron términos de servicio

---

## Contacto

**Autor:** Efren Bohorquez Vargas  
**Institución:** Universidad Central  
**Proyecto:** Big Data - Análisis de Entidades Públicas  
**Fecha:** 19 de noviembre de 2025

---

*Generado automáticamente por el sistema de Web Scraping Ético*
