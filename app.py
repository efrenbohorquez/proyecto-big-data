import logging
import math
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)

# Importación de las clases auxiliares definidas en helpers/__init__.py
from helpers import ElasticSearch, Funciones, Mongo_DB

# --- Setup Inicial ---
load_dotenv() # Carga las variables desde el archivo .env

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Se obtiene la llave secreta del archivo .env para manejar sesiones
app.secret_key = os.getenv('SECRET_KEY', 'default_key_if_not_found') 

# Variables de la aplicación (para pasar a los templates)
version_app = "1.1" # Versión del proyecto
creador_app = "Efren Bohorquez Vargas" # Nombre del creador
universidad_app = "Universidad Central" # Universidad

# Instanciación de variables de entorno para las conexiones
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')
ELASTIC_URL = os.getenv('ELASTIC_CLOUD_URL')
ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY')
UPLOAD_FOLDER = 'uploads'

# Validar que las variables de entorno críticas estén configuradas
if not MONGO_URI or not MONGO_DB_NAME or not MONGO_COLLECTION:
    logger.error("Error: Variables de MongoDB no configuradas en .env")
    raise ValueError("Configuración de MongoDB incompleta. Verifica el archivo .env")

if not ELASTIC_URL or not ELASTIC_API_KEY:
    logger.warning("Advertencia: Variables de ElasticSearch no configuradas, funcionará solo con MongoDB")

# Instanciación de las clases de conexión
mongo_db = Mongo_DB(MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION)
elastic_search = ElasticSearch(ELASTIC_URL or '', ELASTIC_API_KEY or '')
funciones = Funciones()

# --- Rutas de la Aplicación ---

# Ruta de inicio (Landing Page)
@app.route('/', methods=['GET']) 
def landing():
    # Renderiza la página inicial y pasa las variables de versión y creador
    return render_template('landing.html', 
                           version=version_app, 
                           creador=creador_app,
                           universidad=universidad_app)

# Ruta Acerca de (About Page)
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

# Ruta de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica para recibir datos, validar con Mongo y crear sesión
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', version=version_app, error="Usuario y contraseña requeridos")
        
        # TODO: Implementar autenticación con MongoDB y bcrypt
        # Por ahora, mantener credenciales de prueba (CAMBIAR EN PRODUCCIÓN)
        if username == "admin" and password == "admin123": 
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'admin'
            logger.info(f"Usuario '{username}' inició sesión correctamente")
            return redirect(url_for('admin'))
        else:
            logger.warning(f"Intento de login fallido para usuario '{username}'")
            return render_template('login.html', version=version_app, error="Credenciales incorrectas") 
    
    # Si es método GET, mostrar el formulario de login
    return render_template('login.html', version=version_app) 

# Ruta de logout
@app.route('/logout')
def logout():
    """Cerrar sesión del usuario"""
    username = session.get('username', 'Usuario desconocido')
    session.clear()
    logger.info(f"Usuario '{username}' cerró sesión")
    return redirect(url_for('landing'))

# Ruta de Administración (Admin Page) - Requiere Sesión
@app.route('/admin')
def admin():
    # Verifica si hay una sesión activa
    if 'logged_in' not in session or not session.get('logged_in'):
        logger.warning("Intento de acceso no autorizado a /admin")
        return redirect(url_for('login'))
    
    # Lógica para mostrar el panel de administración
    try:
        stats = mongo_db.obtener_estadisticas()
        return render_template('admin.html', 
                             version=version_app,
                             username=session.get('username', 'Admin'),
                             estadisticas=stats)
    except Exception as e:
        logger.error(f"Error al cargar panel admin: {e}")
        return render_template('admin.html', version=version_app, error="Error al cargar datos")

# --- Sistema de Búsqueda de Documentos ---

# Página principal de búsqueda
@app.route('/documentos', methods=['GET'])
def documentos():
    """Página de búsqueda de documentos con filtros y paginación"""
    # Obtener estadísticas para la interfaz
    try:
        estadisticas = mongo_db.obtener_estadisticas()
        docs_recientes = mongo_db.obtener_documentos_recientes(10)
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        estadisticas = {
            'total_documentos': 0,
            'categorias': [],
            'tipos': [],
            'tamano_total': 0
        }
        docs_recientes = []
    
    return render_template('documentos.html', 
                         version=version_app,
                         universidad=universidad_app,
                         creador=creador_app,
                         estadisticas=estadisticas,
                         documentos_recientes=docs_recientes)

# API REST para búsqueda de documentos
@app.route('/api/buscar', methods=['POST'])
def api_buscar_documentos():
    """API REST para búsqueda con ElasticSearch y MongoDB como fallback"""
    try:
        # Obtener parámetros de búsqueda
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        categoria = data.get('categoria', '')
        tipo = data.get('tipo', '')
        pagina = int(data.get('pagina', 1))
        por_pagina = int(data.get('por_pagina', 10))
        orden = data.get('orden', 'relevancia')  # relevancia, fecha_desc, fecha_asc, titulo
        
        # Validaciones
        por_pagina = min(max(por_pagina, 1), 100)  # Límite entre 1 y 100
        pagina = max(pagina, 1)
        
        # Intentar búsqueda con ElasticSearch primero
        usar_elasticsearch = query != ''  # Solo usar ES si hay query de texto
        
        if usar_elasticsearch:
            try:
                resultados = elastic_search.buscar_documentos(query, categoria, tipo, pagina, por_pagina, orden)
                resultados['motor'] = 'elasticsearch'
                return jsonify(resultados)
            except Exception as es_error:
                logger.warning(f"Error en ElasticSearch (fallback a Mongo): {es_error}")
                pass
        
        # Búsqueda con MongoDB (fallback o cuando no hay query)
        # Configurar ordenamiento para Mongo
        if orden == 'fecha_desc':
            sort_config = [('fecha_descarga', -1)]
        elif orden == 'fecha_asc':
            sort_config = [('fecha_descarga', 1)]
        elif orden == 'titulo':
            sort_config = [('titulo', 1)]
        else:  # Por defecto, fecha descendente
            sort_config = [('fecha_descarga', -1)]

        from_doc = (pagina - 1) * por_pagina
        documentos, total = mongo_db.buscar_documentos_con_snippets(query, categoria, tipo, from_doc, por_pagina, sort_config)
        
        total_paginas = math.ceil(total / por_pagina)
        
        resultados = {
            'exito': True,
            'documentos': documentos,
            'total': total,
            'pagina': pagina,
            'por_pagina': por_pagina,
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

# API para obtener detalles de un documento
@app.route('/api/documento/<int:numero>', methods=['GET'])
def api_documento_detalle(numero):
    """Obtener detalles completos de un documento específico"""
    try:
        documento = mongo_db.obtener_documento_por_numero(numero)
        
        if not documento:
            return jsonify({
                'error': 'Documento no encontrado',
                'numero': numero
            }), 404
        
        return jsonify({
            'exito': True,
            'documento': documento
        })
        
    except Exception as e:
        logger.error(f"Error al obtener el documento: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al obtener el documento'
        }), 500

# API para obtener estadísticas
@app.route('/api/estadisticas', methods=['GET'])
def api_estadisticas():
    """Obtener estadísticas generales del sistema"""
    try:
        stats = mongo_db.obtener_estadisticas_avanzadas()
        
        # Obtener total y tamaño para completar
        basic_stats = mongo_db.obtener_estadisticas()
        
        return jsonify({
            'exito': True,
            'total_documentos': basic_stats['total_documentos'],
            'tamano_total_gb': round(basic_stats['tamano_total'] / 1024, 2),
            'categorias': stats.get('categorias', []),
            'tipos': stats.get('tipos', []),
            'años': stats.get('años', [])
        })
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al obtener estadísticas'
        }), 500 

# --- Bloque de Ejecución Principal ---

if __name__ == '__main__':
    
    # Crear la carpeta de uploads si no existe
    funciones.crear_carpeta(UPLOAD_FOLDER) 

    # Probar conexiones (no bloqueantes)
    if not mongo_db.probar_conexion():
        logger.warning("Error al probar conexión a MongoDB, continuando...")
    
    if not elastic_search.probar_conexion():
        logger.warning("Error al probar conexión a ElasticSearch, continuando...")
    
    print("\n" + "="*50)
    print("Servidor Flask iniciado correctamente")
    print("Accede a: http://127.0.0.1:5001")
    print("Sistema de Búsqueda: http://127.0.0.1:5001/documentos")
    print("Presiona CTRL+C para detener")
    print("="*50 + "\n")

    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)
