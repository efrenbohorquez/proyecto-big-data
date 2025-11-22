# Guía de Actualización y Mantenimiento del Repositorio

Esta guía está diseñada para facilitar la actualización de la información del proyecto, dependencias y despliegue en el futuro.

## 1. Actualizar Información del Autor
Si necesitas modificar los datos del autor o la versión del proyecto:

1.  **Backend (`app.py`):**
    Busca las líneas 28-30 y edita los valores:
    ```python
    version_app = "1.3" # Nueva versión
    creador_app = "Nuevo Nombre"
    universidad_app = "Nueva Institución"
    ```

2.  **Documentación (`README.md`):**
    Actualiza la sección de "Autor" al final del archivo.

## 2. Actualizar Dependencias
Si agregas nuevas librerías al proyecto:

1.  Instala la librería localmente:
    ```bash
    pip install nombre_libreria
    ```
2.  Actualiza `requirements.txt` (asegúrate de usar versiones fijas):
    ```bash
    pip freeze > requirements.txt
    ```
    *Nota: Revisa el archivo generado para eliminar librerías del sistema no relacionadas.*

## 3. Subir Cambios al Repositorio (GitHub)
Para guardar tus cambios en la nube:

```bash
# 1. Ver estado de archivos
git status

# 2. Agregar todos los cambios
git add .

# 3. Guardar cambios con un mensaje descriptivo
git commit -m "descripción de los cambios realizados"

# 4. Enviar a GitHub
git push origin main
```

## 4. Actualizar Despliegue en Render
Si tienes configurado el despliegue automático:
*   Al hacer `git push origin main`, Render detectará los cambios y redesplegará automáticamente.

Si necesitas cambiar variables de entorno (como API Keys):
1.  Ve al Dashboard de Render.
2.  Selecciona tu servicio.
3.  Ve a "Environment".
4.  Edita o agrega las variables necesarias.

## 5. Copia de Seguridad de Datos
Para exportar tus datos de MongoDB:
*   Usa MongoDB Compass para conectar a tu cluster.
*   Selecciona la colección `documentos`.
*   Ve a "Collection" > "Export Collection".
*   Guarda el archivo JSON o CSV como respaldo.
