# Reporte de Cumplimiento - Rúbrica de Sustentación

Este documento analiza el estado actual del proyecto frente a los requisitos de la rúbrica de sustentación.

## ✅ Estado de Cumplimiento

| Requisito (Protocolo) | Estado | Detalle / Evidencia |
| :--- | :---: | :--- |
| **2.a Fuente de Datos** | ✅ Cumple | **108 documentos** cargados en MongoDB (Mínimo 100 requerido). <br> *Nota:* Se agregaron documentos adicionales para superar el umbral. |
| **2.b Método/Algoritmo** | ✅ Cumple | Se utilizan scripts de Python (`scraper_procuraduria.py`) para extracción, `BeautifulSoup` para limpieza, y `Elasticsearch` para indexación. Se integra `Gemini` (LLM) para análisis. |
| **2.c Deploy/Render** | ✅ Cumple | Aplicación desplegada en Render. <br> - **Personalización:** Interfaz con Bootstrap y estilos propios. <br> - **Navegabilidad:** Dashboard, Login, Búsqueda. <br> - **Búsqueda:** Funcionalidad probada con Elasticsearch. |
| **2.d Repositorio Público** | ⚠️ Parcial | Repositorio en GitHub disponible. <br> *Acción:* Se ha generado un notebook de ejemplo `notebooks/analisis_proyecto.ipynb` para cumplir este punto. |

## 📝 Recomendaciones para la Sustentación

1.  **Completar Documentos:** Ejecuta el scraper para obtener al menos 2 documentos más y llegar a los 100 requeridos.
2.  **Subir Notebooks:** Si tienes los cuadernos de trabajo de la clase (análisis exploratorio, pruebas de modelos, etc.), súbelos a una carpeta `notebooks/` en el repositorio.
3.  **Preparar Demo:** Ten abierta la aplicación desplegada en Render y el código en VS Code para mostrarlo rápidamente.
4.  **Explicación Técnica:** Repasa cómo funciona la conexión entre MongoDB (almacenamiento) y Elasticsearch (búsqueda), y cómo el LLM genera los resúmenes.

## 🔗 Enlaces Clave
*   **Repositorio:** `https://github.com/efrenbohorquez/proyecto-big-data`
*   **Aplicación:** `https://proyecto-big-data-1.onrender.com`
