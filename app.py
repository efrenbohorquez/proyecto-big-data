import logging
import math
import os
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)

# Importación de las clases auxiliares definidas en helpers/__init__.py
from helpers import ElasticSearch, Funciones, Mongo_DB
from helpers.user_manager import UserManager
from models.user import User

# --- Setup Inicial ---
load_dotenv() # Carga las variables desde el archivo .env

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Se obtiene la llave secreta del archivo .env para manejar sesiones
app.secret_key = os.getenv('SECRET_KEY', 'default_key_if_not_found') 

# Variables de la aplicación (para pasar a los templates)
version_app = "1.2" # Versión del proyecto
creador_app = "Efren Bohorquez Vargas" # Maestría en Analítica de Datos
universidad_app = "Universidad Central" # Proyecto de Grado

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

# Instanciar gestor de usuarios
user_manager = UserManager(mongo_db.client, MONGO_DB_NAME)

# --- Decoradores de Autenticación y Autorización ---

def login_required(f):
    """Decorador para rutas que requieren autenticación."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            logger.warning("Intento de acceso sin autenticación")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(*roles):
    """
    Decorador para rutas que requieren roles específicos.
    
    Uso:
        @require_role('admin')
        @require_role('admin', 'editor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role not in roles:
                logger.warning(f"Usuario con rol '{user_role}' intentó acceder a ruta restringida")
                return jsonify({
                    'error': 'Acceso denegado',
                    'mensaje': f'Se requiere rol: {", ".join(roles)}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
        # Obtener credenciales del formulario
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', version=version_app, error="Usuario y contraseña requeridos")
        
        # Verificar credenciales con UserManager
        user = user_manager.verificar_credenciales(username, password)
        
        if user:
            # Crear sesión
            session['logged_in'] = True
            session['username'] = user.username
            session['user_id'] = user.user_id
            session['role'] = user.rol
            session['nombre_completo'] = user.nombre_completo
            
            logger.info(f"Usuario '{username}' (rol: {user.rol}) inició sesión correctamente")
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

# Ruta de ElasticSearch Admin (En construcción)
@app.route('/admin/elasticsearch')
@login_required
def admin_elasticsearch():
    """Página de administración de Elasticsearch (en construcción)"""
    return render_template('elasticsearch.html', 
                         version=version_app,
                         username=session.get('username', 'Admin'))

# Ruta de Cargar Datos (En construcción)
@app.route('/admin/cargar-datos')
@login_required
def admin_cargar_datos():
    """Página para cargar documentos (en construcción)"""
    return render_template('cargar_datos.html', 
                         version=version_app,
                         username=session.get('username', 'Admin'))

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

# --- API de Gestión de Usuarios ---

# Página de gestión de usuarios
@app.route('/admin/usuarios')
@require_role('admin')
def admin_usuarios():
    """Página de gestión de usuarios (solo admin)"""
    return render_template(
        'usuarios.html',
        version=version_app,
        username=session.get('username'),
        nombre_completo=session.get('nombre_completo', '')
    )

# API: Listar usuarios
@app.route('/api/usuarios', methods=['GET'])
@require_role('admin')
def api_listar_usuarios():
    """Lista usuarios con filtros y paginación"""
    try:
        # Parámetros de consulta
        filtro_rol = request.args.get('rol', '')
        filtro_activo = request.args.get('activo', '')
        busqueda = request.args.get('busqueda', '')
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 20))
        
        # Convertir filtro_activo a booleano
        filtro_activo_bool = None
        if filtro_activo == 'true':
            filtro_activo_bool = True
        elif filtro_activo == 'false':
            filtro_activo_bool = False
        
        # Calcular skip
        skip = (pagina - 1) * por_pagina
        
        # Obtener usuarios
        usuarios, total = user_manager.listar_usuarios(
            filtro_rol=filtro_rol if filtro_rol else None,
            filtro_activo=filtro_activo_bool,
            busqueda=busqueda if busqueda else None,
            skip=skip,
            limit=por_pagina
        )
        
        # Convertir a diccionarios
        usuarios_dict = [user.to_dict() for user in usuarios]
        
        # Calcular total de páginas
        total_paginas = math.ceil(total / por_pagina)
        
        return jsonify({
            'exito': True,
            'usuarios': usuarios_dict,
            'total': total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'total_paginas': total_paginas
        })
        
    except Exception as e:
        logger.error(f"Error al listar usuarios: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al listar usuarios'
        }), 500

# API: Crear usuario
@app.route('/api/usuarios', methods=['POST'])
@require_role('admin')
def api_crear_usuario():
    """Crea un nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['username', 'email', 'password', 'rol']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear usuario
        user = user_manager.crear_usuario(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            rol=data['rol'],
            nombre_completo=data.get('nombre_completo', '')
        )
        
        if user:
            logger.info(f"Usuario '{user.username}' creado por admin '{session.get('username')}'")
            return jsonify({
                'exito': True,
                'mensaje': 'Usuario creado exitosamente',
                'usuario': user.to_dict()
            }), 201
        else:
            return jsonify({
                'error': 'No se pudo crear el usuario',
                'mensaje': 'El username o email ya existe'
            }), 400
            
    except Exception as e:
        logger.error(f"Error al crear usuario: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al crear usuario'
        }), 500

# API: Obtener usuario por ID
@app.route('/api/usuarios/<int:user_id>', methods=['GET'])
@require_role('admin')
def api_obtener_usuario(user_id):
    """Obtiene un usuario por su ID"""
    try:
        user = user_manager.obtener_usuario(user_id)
        
        if user:
            return jsonify({
                'exito': True,
                'usuario': user.to_dict()
            })
        else:
            return jsonify({
                'error': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error al obtener usuario {user_id}: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al obtener usuario'
        }), 500

# API: Actualizar usuario
@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
@require_role('admin')
def api_actualizar_usuario(user_id):
    """Actualiza los datos de un usuario"""
    try:
        data = request.get_json()
        
        # Actualizar usuario
        success = user_manager.actualizar_usuario(user_id, data)
        
        if success:
            logger.info(f"Usuario {user_id} actualizado por admin '{session.get('username')}'")
            return jsonify({
                'exito': True,
                'mensaje': 'Usuario actualizado exitosamente'
            })
        else:
            return jsonify({
                'error': 'No se pudo actualizar el usuario'
            }), 400
            
    except Exception as e:
        logger.error(f"Error al actualizar usuario {user_id}: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al actualizar usuario'
        }), 500

# API: Eliminar usuario
@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
@require_role('admin')
def api_eliminar_usuario(user_id):
    """Elimina un usuario"""
    try:
        # No permitir eliminar el propio usuario
        if user_id == session.get('user_id'):
            return jsonify({
                'error': 'No puedes eliminar tu propio usuario'
            }), 400
        
        success = user_manager.eliminar_usuario(user_id)
        
        if success:
            logger.info(f"Usuario {user_id} eliminado por admin '{session.get('username')}'")
            return jsonify({
                'exito': True,
                'mensaje': 'Usuario eliminado exitosamente'
            })
        else:
            return jsonify({
                'error': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error al eliminar usuario {user_id}: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al eliminar usuario'
        }), 500

# API: Cambiar rol de usuario
@app.route('/api/usuarios/<int:user_id>/rol', methods=['POST'])
@require_role('admin')
def api_cambiar_rol(user_id):
    """Cambia el rol de un usuario"""
    try:
        data = request.get_json()
        nuevo_rol = data.get('rol')
        
        if not nuevo_rol:
            return jsonify({
                'error': 'Rol requerido'
            }), 400
        
        # No permitir cambiar el rol del propio usuario
        if user_id == session.get('user_id'):
            return jsonify({
                'error': 'No puedes cambiar tu propio rol'
            }), 400
        
        success = user_manager.cambiar_rol(user_id, nuevo_rol)
        
        if success:
            logger.info(f"Rol del usuario {user_id} cambiado a '{nuevo_rol}' por admin '{session.get('username')}'")
            return jsonify({
                'exito': True,
                'mensaje': f'Rol cambiado a {nuevo_rol} exitosamente'
            })
        else:
            return jsonify({
                'error': 'No se pudo cambiar el rol'
            }), 400
            
    except Exception as e:
        logger.error(f"Error al cambiar rol del usuario {user_id}: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al cambiar rol'
        }), 500

# API: Cambiar contraseña
@app.route('/api/usuarios/<int:user_id>/password', methods=['POST'])
@require_role('admin')
def api_cambiar_password(user_id):
    """Cambia la contraseña de un usuario"""
    try:
        data = request.get_json()
        nueva_password = data.get('password')
        
        if not nueva_password:
            return jsonify({
                'error': 'Contraseña requerida'
            }), 400
        
        if len(nueva_password) < 6:
            return jsonify({
                'error': 'La contraseña debe tener al menos 6 caracteres'
            }), 400
        
        success = user_manager.cambiar_password(user_id, nueva_password)
        
        if success:
            logger.info(f"Contraseña del usuario {user_id} cambiada por admin '{session.get('username')}'")
            return jsonify({
                'exito': True,
                'mensaje': 'Contraseña cambiada exitosamente'
            })
        else:
            return jsonify({
                'error': 'No se pudo cambiar la contraseña'
            }), 400
            
    except Exception as e:
        logger.error(f"Error al cambiar contraseña del usuario {user_id}: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al cambiar contraseña'
        }), 500

# API: Estadísticas de usuarios
@app.route('/api/usuarios/estadisticas', methods=['GET'])
@require_role('admin')
def api_estadisticas_usuarios():
    """Obtiene estadísticas de usuarios"""
    try:
        conteo_por_rol = user_manager.contar_usuarios_por_rol()
        usuarios, total = user_manager.listar_usuarios(skip=0, limit=1)
        
        return jsonify({
            'exito': True,
            'total_usuarios': total,
            'por_rol': conteo_por_rol
        })
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de usuarios: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error al obtener estadísticas'
        }), 500

# --- API de Búsqueda Avanzada ---

# API: Búsqueda con agregaciones
@app.route('/api/buscar-avanzada', methods=['GET'])
def api_buscar_avanzada():
    """Búsqueda avanzada con agregaciones y filtros dinámicos"""
    try:
        query = request.args.get('query', '').strip()
        categoria = request.args.get('categoria', '').strip()
        tipo = request.args.get('tipo', '').strip()
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 10))
        orden = request.args.get('orden', 'relevancia')
        
        # Intentar con Elasticsearch primero
        if elastic_search.client and query:
            try:
                resultados = elastic_search.buscar_con_agregaciones(
                    query, categoria, tipo, pagina, por_pagina, orden
                )
                resultados['motor'] = 'elasticsearch'
                return jsonify(resultados)
            except Exception as es_error:
                logger.warning(f"Error en ElasticSearch avanzado: {es_error}")
                pass
        
        # Fallback a MongoDB
        from_doc = (pagina - 1) * por_pagina
        
        if orden == 'fecha_desc':
            sort_config = [('fecha_descarga', -1)]
        elif orden == 'fecha_asc':
            sort_config = [('fecha_descarga', 1)]
        elif orden == 'titulo':
            sort_config = [('titulo', 1)]
        else:
            sort_config = [('fecha_descarga', -1)]
        
        documentos, total = mongo_db.buscar_documentos_con_snippets(
            query, categoria, tipo, from_doc, por_pagina, sort_config
        )
        
        total_paginas = math.ceil(total / por_pagina)
        
        return jsonify({
            'exito': True,
            'documentos': documentos,
            'total': total,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'total_paginas': total_paginas,
            'query': query,
            'motor': 'mongodb',
            'agregaciones': {
                'categorias': [],
                'tipos': [],
                'años': []
            }
        })
        
    except Exception as e:
        logger.error(f"Error en búsqueda avanzada: {e}")
        return jsonify({
            'error': str(e),
            'mensaje': 'Error en búsqueda avanzada'
        }), 500

from helpers.llm_service import llm_service

# ... (existing imports)

# API: Sugerencias de autocompletado
@app.route('/api/sugerencias', methods=['GET'])
def api_sugerencias():
    # ... (existing code)
    pass # Placeholder to match context, actual replacement below

# API: Analizar documento con IA
@app.route('/api/analizar-documento', methods=['POST'])
def api_analizar_documento():
    """Genera un resumen del documento usando IA"""
    try:
        data = request.get_json()
        doc_id = data.get('id')
        
        if not doc_id:
            return jsonify({'exito': False, 'mensaje': 'ID de documento requerido'}), 400
            
        # Obtener documento de la BD
        doc = mongo_db.obtener_documento_por_numero(int(doc_id))
        
        if not doc:
            return jsonify({'exito': False, 'mensaje': 'Documento no encontrado'}), 404
            
        texto = doc.get('texto_contenido', '')
        
        if not texto:
            return jsonify({'exito': False, 'mensaje': 'El documento no tiene contenido de texto extraído'}), 400
            
        # Generar resumen
        resumen = llm_service.generar_resumen(texto)
        
        return jsonify({
            'exito': True,
            'resumen': resumen
        })
        
    except Exception as e:
        logger.error(f"Error en análisis de documento: {e}")
        return jsonify({
            'exito': False,
            'mensaje': f'Error interno: {str(e)}'
        }), 500
    """Obtiene sugerencias de autocompletado"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        
        if not query or len(query) < 2:
            return jsonify({
                'exito': True,
                'sugerencias': []
            })
        
        # Intentar con Elasticsearch
        if elastic_search.client:
            try:
                sugerencias = elastic_search.obtener_sugerencias(query, limit)
                return jsonify({
                    'exito': True,
                    'sugerencias': sugerencias
                })
            except Exception as es_error:
                logger.warning(f"Error en sugerencias ES: {es_error}")
        
        # Fallback: buscar en MongoDB
        documentos, _ = mongo_db.buscar_documentos_con_snippets(
            query, '', '', 0, limit, [('fecha_descarga', -1)]
        )
        
        sugerencias = [doc.get('titulo', '') for doc in documentos if doc.get('titulo')]
        
        return jsonify({
            'exito': True,
            'sugerencias': sugerencias[:limit]
        })
        
    except Exception as e:
        logger.error(f"Error al obtener sugerencias: {e}")
        return jsonify({
            'exito': True,
            'sugerencias': []
        })

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
