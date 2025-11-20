# Historial de Cambios

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.1.0] - 2025-11-20

### Añadido
- Modal para ver detalles completos de documentos
- Sistema de estadísticas en tiempo real
- Panel de administración con dashboard
- Validación de variables de entorno al iniciar
- Scripts de utilidad (crear_usuario_admin.py, generar_reporte.py)
- Configuración de VS Code con launch.json y settings.json
- Archivo .gitignore completo
- Archivo .env.example como plantilla
- Documentación CONTRIBUTING.md
- Archivo LICENSE con licencia MIT
- Ruta /logout para cerrar sesión

### Cambiado
- Mejorada la interfaz de búsqueda de documentos
- Actualizado README.md con documentación completa
- Refactorizado sistema de autenticación con validación
- Mejorado manejo de errores con logging detallado
- Optimizada visualización de estadísticas

### Corregido
- Error de tipo None en variables de entorno
- Configuración incorrecta de MONGO_COLLECTION
- Estadísticas no se mostraban en la interfaz
- Botón "Ver Detalles" sin funcionalidad
- Problemas de sesión en panel de administración

### Seguridad
- Añadida validación de variables de entorno obligatorias
- Implementado logging de eventos de seguridad
- Mejorada gestión de sesiones Flask

## [1.0.0] - 2025-11-19

### Añadido
- Sistema de búsqueda con ElasticSearch
- Base de datos MongoDB Atlas
- API REST para búsqueda de documentos
- Web scraping ético de Procuraduría
- Interfaz web responsive con Bootstrap 5
- Sistema de autenticación básico
- Paginación de resultados
- Filtros por categoría y tipo
- Múltiples opciones de ordenamiento

### Funcionalidades Principales
- Búsqueda inteligente de texto completo
- Fallback automático MongoDB/ElasticSearch
- 98 documentos indexados
- 6 categorías de documentos
- 3 tipos de archivo soportados
- Panel de administración

---

## Tipos de cambios

- **Añadido** para funcionalidades nuevas
- **Cambiado** para cambios en funcionalidades existentes
- **Deprecado** para funcionalidades que serán eliminadas
- **Eliminado** para funcionalidades eliminadas
- **Corregido** para corrección de bugs
- **Seguridad** para vulnerabilidades corregidas
