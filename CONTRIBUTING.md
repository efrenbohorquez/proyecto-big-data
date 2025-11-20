# Guía de Contribución

Gracias por tu interés en contribuir al Proyecto Big Data. Este documento proporciona pautas para contribuir al proyecto.

## 🤝 Código de Conducta

Al participar en este proyecto, aceptas mantener un ambiente respetuoso y colaborativo. Se espera que todos los contribuyentes:

- Sean respetuosos y considerados
- Acepten críticas constructivas
- Se enfoquen en lo mejor para la comunidad
- Muestren empatía hacia otros miembros

## 🚀 Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor crea un issue con:

1. **Título descriptivo**
2. **Descripción detallada** del problema
3. **Pasos para reproducir** el error
4. **Comportamiento esperado** vs **comportamiento actual**
5. **Capturas de pantalla** (si aplica)
6. **Información del entorno** (OS, Python version, etc.)

### Sugerir Mejoras

Para sugerir nuevas funcionalidades:

1. **Verifica** que no exista ya un issue similar
2. **Describe claramente** la funcionalidad propuesta
3. **Explica por qué** sería útil para el proyecto
4. **Proporciona ejemplos** de uso si es posible

### Pull Requests

1. **Fork el repositorio**
```bash
git clone https://github.com/efrenbohorquez/proyecto-big-data.git
```

2. **Crea una rama** para tu feature
```bash
git checkout -b feature/nueva-funcionalidad
```

3. **Realiza tus cambios**
   - Sigue las normas de código
   - Añade tests si es necesario
   - Actualiza la documentación

4. **Commit tus cambios**
```bash
git commit -m "feat: descripción clara del cambio"
```

5. **Push a tu fork**
```bash
git push origin feature/nueva-funcionalidad
```

6. **Abre un Pull Request**
   - Describe qué cambios realizaste
   - Referencia issues relacionados
   - Incluye capturas si aplica

## 📝 Estándares de Código

### Python

- **PEP 8**: Seguir la guía de estilo de Python
- **Type Hints**: Usar anotaciones de tipo
- **Docstrings**: Documentar funciones y clases

```python
def buscar_documentos(query: str, categoria: str) -> List[Dict]:
    """
    Busca documentos en la base de datos.
    
    Args:
        query: Término de búsqueda
        categoria: Categoría de documentos
        
    Returns:
        Lista de documentos encontrados
    """
    pass
```

- **Nombres descriptivos**: Variables y funciones con nombres claros
- **Funciones pequeñas**: Máximo 50 líneas por función
- **Imports organizados**: stdlib, third-party, local

### JavaScript

- **ES6+**: Usar sintaxis moderna
- **camelCase**: Para variables y funciones
- **Comentarios**: Documentar lógica compleja

### HTML/CSS

- **Indentación**: 4 espacios
- **Semántica**: Usar etiquetas HTML5 apropiadas
- **Clases Bootstrap**: Aprovechar framework

## 📋 Convenciones de Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>: <descripción>

[cuerpo opcional]

[footer opcional]
```

### Tipos de Commits

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato, punto y coma faltantes, etc.
- `refactor`: Refactorización de código
- `test`: Añadir o modificar tests
- `chore`: Cambios en build, dependencies, etc.
- `perf`: Mejoras de rendimiento

### Ejemplos

```bash
feat: agregar búsqueda por rango de fechas

fix: corregir error en paginación de resultados

docs: actualizar guía de instalación

refactor: extraer lógica de conexión a MongoDB
```

## 🧪 Tests

Antes de enviar un PR:

1. **Ejecuta todos los tests**
```bash
pytest
```

2. **Verifica cobertura**
```bash
pytest --cov=.
```

3. **Añade tests** para nuevas funcionalidades

## 📚 Documentación

Al añadir funcionalidades:

1. **Actualiza README.md** si es necesario
2. **Documenta funciones** con docstrings
3. **Actualiza comentarios** si cambias lógica
4. **Añade ejemplos** de uso

## 🔍 Revisión de Código

Los Pull Requests serán revisados considerando:

- Cumplimiento de estándares de código
- Tests adecuados
- Documentación actualizada
- Funcionalidad correcta
- Sin breaking changes innecesarios

## ❓ Preguntas

Si tienes dudas:

1. Revisa la documentación existente
2. Busca en issues cerrados
3. Abre un nuevo issue con la etiqueta `question`

## 🎯 Áreas de Contribución

Puedes contribuir en:

- 🐛 **Corrección de bugs**
- ✨ **Nuevas funcionalidades**
- 📝 **Documentación**
- 🧪 **Tests**
- 🎨 **Mejoras de UI/UX**
- ⚡ **Optimización de rendimiento**
- 🌐 **Internacionalización**

## 📋 Checklist para PR

Antes de enviar tu Pull Request:

- [ ] El código sigue los estándares del proyecto
- [ ] Los tests pasan correctamente
- [ ] La documentación está actualizada
- [ ] Los commits siguen las convenciones
- [ ] No hay conflictos con la rama main
- [ ] Has probado localmente los cambios

## 🙏 Agradecimientos

¡Gracias por contribuir al Proyecto Big Data! Tu ayuda es muy valiosa para mejorar este proyecto.

---

**Última actualización**: Noviembre 2025
