# Guía de Despliegue en Render

## Índice

- [Prerrequisitos](#prerrequisitos)
- [Preparación del Proyecto](#preparación-del-proyecto)
- [Configuración en Render](#configuración-en-render)
- [Variables de Entorno](#variables-de-entorno)
- [Despliegue](#despliegue)
- [Verificación](#verificación)
- [Troubleshooting](#troubleshooting)

## Prerrequisitos

Antes de desplegar en Render, asegúrate de tener:

### 1. Cuentas Necesarias

- ✅ Cuenta de GitHub (https://github.com)
- ✅ Cuenta de Render (https://render.com)
- ✅ Cuenta de MongoDB Atlas (https://cloud.mongodb.com)
- ✅ Cuenta de ElasticSearch Cloud (https://cloud.elastic.co)

### 2. Servicios Configurados

- ✅ Base de datos MongoDB Atlas funcionando
- ✅ Cluster ElasticSearch activo
- ✅ Documentos indexados en ambas bases de datos

### 3. Repositorio GitHub

- ✅ Proyecto subido a GitHub
- ✅ Archivo `requirements.txt` actualizado
- ✅ Archivo `.gitignore` configurado
- ✅ Archivo `README.md` completo

## Preparación del Proyecto

### 1. Verificar Archivos Esenciales

Asegúrate de que tu proyecto tenga estos archivos:

```
proyecto-big-data/
├── app.py                  ✅ Aplicación principal
├── requirements.txt        ✅ Dependencias Python
├── .gitignore             ✅ Archivos ignorados
├── .env.example           ✅ Template de variables
├── README.md              ✅ Documentación
├── helpers/               ✅ Módulos auxiliares
│   ├── __init__.py
│   ├── mongo_db.py
│   ├── elasticsearch.py
│   ├── funciones.py
│   └── web_scraper.py
└── templates/             ✅ Templates HTML
    ├── landing.html
    ├── login.html
    ├── documentos.html
    └── admin.html
```

### 2. Verificar `requirements.txt`

El archivo debe contener todas las dependencias:

```txt
Flask==3.0.0
pymongo==4.6.0
elasticsearch==8.11.0
bcrypt==4.0.1
gunicorn==21.2.0
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
```

### 3. Verificar Configuración de Producción

En `app.py`, asegúrate de tener:

```python
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# NO ACTIVAR DEBUG EN PRODUCCIÓN
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## Configuración en Render

### 1. Crear Cuenta en Render

1. Ve a https://render.com
2. Haz clic en "Get Started"
3. Regístrate con GitHub (recomendado)

### 2. Conectar Repositorio GitHub

1. En el Dashboard de Render, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu cuenta de GitHub si aún no lo has hecho
4. Busca y selecciona el repositorio `proyecto-big-data`
5. Haz clic en "Connect"

### 3. Configurar el Web Service

Completa el formulario con estos valores:

#### Información Básica

| Campo | Valor |
|-------|-------|
| **Name** | `proyecto-big-data` |
| **Region** | `Oregon (US West)` (o el más cercano) |
| **Branch** | `main` |
| **Root Directory** | (dejar en blanco) |
| **Runtime** | `Python 3` |

#### Build & Deploy

| Campo | Valor |
|-------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

#### Plan

| Campo | Valor |
|-------|-------|
| **Instance Type** | `Free` (para desarrollo) |

> **Nota**: El plan gratuito tiene limitaciones:
> - Se duerme después de 15 minutos de inactividad
> - Límite de 750 horas/mes
> - Para producción, considera el plan Starter ($7/mes)

## Variables de Entorno

### 1. Configurar Variables en Render

En la sección "Environment" del formulario, añade estas variables:

#### Variables Obligatorias

```bash
# Flask
SECRET_KEY=tu-clave-secreta-super-segura-aqui
PORT=10000

# MongoDB Atlas
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=proyecto_big_data
MONGO_COLLECTION=documentos_procuraduria

# ElasticSearch Cloud
ELASTIC_URL=https://tu-cluster.es.us-central1.gcp.cloud.es.io
ELASTIC_API_KEY=tu-api-key-de-elasticsearch
```

#### Obtener Credenciales

**MongoDB Atlas**:
1. Ve a https://cloud.mongodb.com
2. Selecciona tu cluster
3. Haz clic en "Connect"
4. Selecciona "Connect your application"
5. Copia la cadena de conexión y reemplaza `<password>`

**ElasticSearch Cloud**:
1. Ve a https://cloud.elastic.co
2. Selecciona tu deployment
3. Ve a "API Keys"
4. Crea una nueva API Key o usa una existente
5. Copia la URL del cluster y la API Key

**SECRET_KEY**:
Genera una clave segura con Python:

```python
import secrets
print(secrets.token_hex(32))
```

### 2. Verificar Variables

Después de añadir todas las variables, verifica que:

- ✅ No hay espacios antes/después de los valores
- ✅ Las URLs tienen el protocolo correcto (`https://`, `mongodb+srv://`)
- ✅ Las contraseñas no tienen caracteres especiales sin codificar
- ✅ El SECRET_KEY es diferente al de desarrollo

## Despliegue

### 1. Iniciar el Despliegue

1. Revisa toda la configuración
2. Haz clic en "Create Web Service"
3. Render comenzará a desplegar automáticamente

### 2. Monitorear el Despliegue

En la página del servicio, verás:

```
┌────────────────────────────────────┐
│  🔄 Build in progress...           │
│  ─────────────────────────────     │
│  Installing dependencies...        │
│  Collecting Flask==3.0.0           │
│  Collecting pymongo==4.6.0         │
│  ...                               │
└────────────────────────────────────┘
```

El proceso toma aproximadamente 2-5 minutos.

### 3. Build Exitoso

Si el build es exitoso, verás:

```
┌────────────────────────────────────┐
│  ✅ Build succeeded                │
│  🚀 Deploy live                    │
│  Your service is live at:          │
│  https://proyecto-big-data.onrender.com
└────────────────────────────────────┘
```

## Verificación

### 1. Verificar Servicio

Accede a tu aplicación:

```
https://tu-app-name.onrender.com
```

Deberías ver la página de inicio (landing page).

### 2. Probar Funcionalidades

#### Test 1: Login

1. Ve a `/login`
2. Ingresa credenciales: `admin` / `admin123`
3. Deberías ser redirigido a `/documentos`

#### Test 2: Búsqueda

1. En la página de documentos
2. Busca: "código"
3. Deberías ver resultados de la base de datos

#### Test 3: Estadísticas

1. Ve a `/admin`
2. Deberías ver las estadísticas:
   - Total documentos: 98
   - Categorías: 6
   - Tamaño total: 527 MB

### 3. Revisar Logs

En el Dashboard de Render:

1. Ve a la pestaña "Logs"
2. Busca mensajes como:

```
INFO: Connected to MongoDB successfully
INFO: Connected to ElasticSearch successfully
INFO: Application started on port 10000
```

Si ves errores, revisa la sección [Troubleshooting](#troubleshooting).

## Troubleshooting

### Error: "Application failed to start"

**Problema**: La aplicación no inicia.

**Solución**:
1. Revisa los logs en Render
2. Verifica que `requirements.txt` esté completo
3. Asegúrate de que el Start Command sea correcto: `gunicorn app:app`

### Error: "Cannot connect to MongoDB"

**Problema**: No puede conectarse a MongoDB Atlas.

**Solución**:
1. Verifica que `MONGO_URI` esté correcta
2. En MongoDB Atlas, ve a "Network Access"
3. Añade la IP: `0.0.0.0/0` (permitir todas las IPs)
4. Verifica que el usuario de BD tenga permisos

### Error: "ElasticSearch connection timeout"

**Problema**: ElasticSearch no responde.

**Solución**:
1. Verifica que `ELASTIC_URL` y `ELASTIC_API_KEY` sean correctas
2. En Elastic Cloud, verifica que el deployment esté activo
3. Revisa el plan de ElasticSearch (free tier tiene límites)

### Error: "Secret key is required"

**Problema**: Falta la SECRET_KEY.

**Solución**:
1. Ve a Environment Variables en Render
2. Añade `SECRET_KEY` con un valor seguro
3. Guarda y redespliega

### Error: "Module not found"

**Problema**: Falta una dependencia.

**Solución**:
1. Verifica que `requirements.txt` tenga todas las dependencias
2. Verifica que no haya errores de tipeo en los nombres
3. Commit y push los cambios a GitHub
4. Render redespliegará automáticamente

### Servicio se Duerme (Plan Free)

**Problema**: En el plan gratuito, el servicio se duerme después de 15 minutos.

**Solución Temporal**:
- La primera petición tomará ~30 segundos (cold start)

**Solución Permanente**:
- Upgradea al plan Starter ($7/mes)
- O usa un servicio de ping (ej: UptimeRobot) cada 14 minutos

### Redeploy Manual

Si necesitas redesplegar manualmente:

1. Ve al Dashboard de Render
2. Selecciona tu servicio
3. Haz clic en "Manual Deploy"
4. Selecciona la rama (`main`)
5. Haz clic en "Deploy"

## Actualizaciones Futuras

### Despliegue Automático

Render está configurado para auto-deploy:

1. Haces cambios en el código
2. Commit y push a GitHub:
   ```bash
   git add .
   git commit -m "feat: nueva funcionalidad"
   git push origin main
   ```
3. Render detecta el push y redespliega automáticamente

### Rollback

Si algo sale mal después de un deploy:

1. Ve a la pestaña "Events" en Render
2. Encuentra el deploy anterior exitoso
3. Haz clic en "Rollback to this deploy"

## Monitoreo en Producción

### Métricas de Render

Render proporciona:

- **CPU Usage**: Uso de CPU
- **Memory Usage**: Uso de memoria
- **Request Count**: Número de peticiones
- **Response Times**: Tiempos de respuesta

Accede en: Dashboard → tu servicio → Metrics

### Logs en Tiempo Real

Para ver logs en vivo:

1. Dashboard → tu servicio → Logs
2. O usa Render CLI:
   ```bash
   render logs -f
   ```

## Mejores Prácticas

### ✅ DO (Hacer)

- Usa variables de entorno para credenciales
- Mantén `requirements.txt` actualizado
- Desactiva debug en producción
- Usa SECRET_KEY seguro y único
- Monitorea logs regularmente
- Haz backups de MongoDB

### ❌ DON'T (No Hacer)

- No hagas commit de `.env`
- No uses `debug=True` en producción
- No expongas credenciales en el código
- No ignores errores en los logs
- No uses el mismo SECRET_KEY en dev y prod

## Recursos Adicionales

- **Documentación Render**: https://render.com/docs
- **Render Status**: https://status.render.com
- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com
- **ElasticSearch Docs**: https://www.elastic.co/guide

---

**Última actualización**: Noviembre 2025

¿Necesitas ayuda? Abre un issue en GitHub: https://github.com/efrenbohorquez/proyecto-big-data/issues
