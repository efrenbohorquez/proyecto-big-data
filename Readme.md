# Proyecto Big Data - Sistema de Búsqueda Inteligente de Documentos

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![ElasticSearch](https://img.shields.io/badge/ElasticSearch-8.11.0-orange.svg)](https://www.elastic.co/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Descripción

Sistema web de búsqueda inteligente de documentos utilizando arquitectura híbrida MongoDB + ElasticSearch. Desarrollado como proyecto de la Maestría en Analítica de la Universidad Central.

**Autor:** Efren Bohorquez Vargas  
**Versión:** 1.1  
**Fecha:** Noviembre 2025

## 🌟 Características Principales

- ✅ **Búsqueda Inteligente**: Motor de búsqueda avanzado con ElasticSearch
- ✅ **Arquitectura Híbrida**: MongoDB + ElasticSearch con fallback automático
- ✅ **API REST**: Endpoints JSON para integración
- ✅ **Panel de Administración**: Dashboard con estadísticas en tiempo real
- ✅ **Web Scraping Ético**: Extracción responsable de datos públicos
- ✅ **Responsive Design**: Interfaz moderna con Bootstrap 5
- ✅ **Sistema de Autenticación**: Login seguro con sesiones

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 3.0.0** - Framework web
- **Python 3.10+** - Lenguaje de programación
- **pymongo 4.6.0** - Driver MongoDB
- **elasticsearch 8.11.0** - Cliente ElasticSearch
- **bcrypt 4.0.1** - Hashing de contraseñas
- **python-dotenv 1.0.0** - Variables de entorno

### Frontend
- **Bootstrap 5.3** - Framework CSS
- **Font Awesome 6.4** - Iconos
- **JavaScript ES6** - Interactividad

### Bases de Datos
- **MongoDB Atlas** - Base de datos NoSQL
- **ElasticSearch Cloud** - Motor de búsqueda

### DevOps
- **Gunicorn 21.2.0** - Servidor WSGI
- **Git** - Control de versiones
- **Render** - Plataforma de despliegue

## 📦 Instalación Local

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git
- Cuenta en MongoDB Atlas (gratuita)
- Cuenta en ElasticSearch Cloud (opcional)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/efrenbohorquez/proyecto-big-data.git
cd proyecto-big-data
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
```

3. **Activar entorno virtual**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
```

6. **Verificar conexiones**
```bash
python verificar_conexiones.py
```

7. **Ejecutar aplicación**
```bash
python app.py
```

8. **Acceder a la aplicación**
```
http://127.0.0.1:5001
```

## 🚀 Despliegue en Render

### Configuración

1. **Crear servicio en Render**: https://render.com

2. **Configuración del Web Service**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3

3. **Variables de Entorno** (en Render Dashboard):
   ```
   MONGO_URI=mongodb+srv://...
   MONGO_DB=proyecto_big_data
   MONGO_COLLECTION=documentos_procuraduria
   ELASTIC_CLOUD_URL=https://...
   ELASTIC_API_KEY=...
   SECRET_KEY=tu_clave_secreta_aqui
   ```

## 📁 Estructura del Proyecto

```
proyecto-big-data/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template variables de entorno
├── .gitignore                      # Archivos ignorados por Git
├── README.md                       # Documentación principal
│
├── helpers/                        # Módulos auxiliares
│   ├── mongo_db.py                # Operaciones MongoDB
│   ├── elasticsearch.py           # Operaciones ElasticSearch
│   ├── funciones.py               # Funciones utilitarias
│   └── web_scraper.py             # Web scraping ético
│
├── templates/                      # Plantillas HTML
│   ├── landing.html               # Página principal
│   ├── login.html                 # Página de login
│   ├── admin.html                 # Panel administración
│   ├── documentos.html            # Búsqueda de documentos
│   └── about.html                 # Acerca de
│
├── uploads/                        # Archivos cargados
└── .github/                        # Configuración GitHub
    └── copilot-instructions.md    # Instrucciones Copilot
```

## 🔌 API REST

### `POST /api/buscar`
Búsqueda de documentos con filtros

**Request:**
```json
{
  "query": "manual",
  "categoria": "Manuales y Procedimientos",
  "tipo": "PDF",
  "pagina": 1,
  "por_pagina": 10
}
```

### `GET /api/documento/<numero>`
Obtener detalles de un documento

### `GET /api/estadisticas`
Estadísticas del sistema

## 📊 Estadísticas del Proyecto

- **98 documentos** indexados
- **6 categorías** de documentos
- **3 tipos de archivo** (PDF, DOC, DOCX)
- **527 MB** de datos procesados

## 🔐 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Sesiones seguras con Flask
- ✅ Validación de entrada
- ⚠️ Cambiar credenciales por defecto: `admin/admin123`

## 🤝 Contribución

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Convenciones de Commits

```
feat: nueva funcionalidad
fix: corrección de bugs
docs: documentación
style: formato de código
refactor: refactorización
test: pruebas
chore: mantenimiento
```

## 📝 Normas de Desarrollo

- **PEP 8** para Python
- **Type hints** en funciones
- **Docstrings** en clases y métodos
- **Nombres descriptivos** de variables
- **Commits descriptivos**

## 📄 Licencia

# Proyecto Big Data - Buscador Inteligente de Documentos

**Autor:** Efren Bohorquez Vargas  
**Contexto:** Maestría en Analítica de Datos - Universidad Central  
**Propósito:** Proyecto de Grado / Caso de Estudio

## Descripción
Este proyecto implementa un sistema de búsqueda y análisis de documentos legales utilizando tecnologías de Big Data como Elasticsearch, MongoDB y Modelos de Lenguaje (LLM).

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.10+** - Lenguaje de programación
- **Flask 2.3.2** - Microframework web
- **bcrypt 4.0.1** - Hashing de contraseñas
- **python-dotenv 1.0.0** - Variables de entorno

### Frontend
- **Bootstrap 5.3** - Framework CSS
- **Font Awesome 6.4** - Iconos
- **JavaScript ES6** - Interactividad

### Bases de Datos
- **MongoDB Atlas** - Base de datos NoSQL
- **ElasticSearch Cloud** - Motor de búsqueda

### DevOps
- **Gunicorn 21.2.0** - Servidor WSGI
- **Git** - Control de versiones
- **Render** - Plataforma de despliegue

## 📦 Instalación Local

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git
- Cuenta en MongoDB Atlas (gratuita)
- Cuenta en ElasticSearch Cloud (opcional)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/efrenbohorquez/proyecto-big-data.git
cd proyecto-big-data
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
```

3. **Activar entorno virtual**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
```

6. **Verificar conexiones**
```bash
python verificar_conexiones.py
```

7. **Ejecutar aplicación**
```bash
python app.py
```

8. **Acceder a la aplicación**
```
http://127.0.0.1:5001
```

## 🚀 Despliegue en Render

### Configuración

1. **Crear servicio en Render**: https://render.com

2. **Configuración del Web Service**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3

3. **Variables de Entorno** (en Render Dashboard):
   ```
   MONGO_URI=mongodb+srv://...
   MONGO_DB=proyecto_big_data
   MONGO_COLLECTION=documentos_procuraduria
   ELASTIC_CLOUD_URL=https://...
   ELASTIC_API_KEY=...
   SECRET_KEY=tu_clave_secreta_aqui
   ```

## 📁 Estructura del Proyecto

```
proyecto-big-data/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias Python
├── .env.example                    # Template variables de entorno
├── .gitignore                      # Archivos ignorados por Git
├── README.md                       # Documentación principal
│
├── helpers/                        # Módulos auxiliares
│   ├── mongo_db.py                # Operaciones MongoDB
│   ├── elasticsearch.py           # Operaciones ElasticSearch
│   ├── funciones.py               # Funciones utilitarias
│   └── web_scraper.py             # Web scraping ético
│
├── templates/                      # Plantillas HTML
│   ├── landing.html               # Página principal
│   ├── login.html                 # Página de login
│   ├── admin.html                 # Panel administración
│   ├── documentos.html            # Búsqueda de documentos
│   └── about.html                 # Acerca de
│
├── uploads/                        # Archivos cargados
└── .github/                        # Configuración GitHub
    └── copilot-instructions.md    # Instrucciones Copilot
```

## 🔌 API REST

### `POST /api/buscar`
Búsqueda de documentos con filtros

**Request:**
```json
{
  "query": "manual",
  "categoria": "Manuales y Procedimientos",
  "tipo": "PDF",
  "pagina": 1,
  "por_pagina": 10
}
```

### `GET /api/documento/<numero>`
Obtener detalles de un documento

### `GET /api/estadisticas`
Estadísticas del sistema

## 📊 Estadísticas del Proyecto

- **98 documentos** indexados
- **6 categorías** de documentos
- **3 tipos de archivo** (PDF, DOC, DOCX)
- **527 MB** de datos procesados

## 🔐 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Sesiones seguras con Flask
- ✅ Validación de entrada
- ⚠️ Cambiar credenciales por defecto: `admin/admin123`

## 🤝 Contribución

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Convenciones de Commits

```
feat: nueva funcionalidad
fix: corrección de bugs
docs: documentación
style: formato de código
refactor: refactorización
test: pruebas
chore: mantenimiento
```

## 📝 Normas de Desarrollo

- **PEP 8** para Python
- **Type hints** en funciones
- **Docstrings** en clases y métodos
- **Nombres descriptivos** de variables
- **Commits descriptivos**

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🙏 Agradecimientos

- Universidad Central
- Procuraduría General de la Nación
- Comunidad open source

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub!**
