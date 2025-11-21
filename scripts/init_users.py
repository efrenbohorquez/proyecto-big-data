"""
Script de inicialización para crear el usuario administrador por defecto.
Ejecutar una sola vez al configurar el sistema por primera vez.
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.user_manager import UserManager
from models.user import User

# Cargar variables de entorno
load_dotenv()

def inicializar_usuario_admin():
    """Crea el usuario administrador por defecto si no existe."""
    
    # Obtener configuración de MongoDB
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB', 'proyecto_big_data')
    
    if not MONGO_URI:
        print("❌ Error: MONGO_URI no configurado en .env")
        return False
    
    try:
        # Conectar a MongoDB
        print("📡 Conectando a MongoDB...")
        client = MongoClient(MONGO_URI)
        user_manager = UserManager(client, MONGO_DB_NAME)
        
        # Verificar si ya existe un usuario admin
        admin_existente = user_manager.obtener_usuario_por_username('admin')
        
        if admin_existente:
            print("⚠️  El usuario 'admin' ya existe.")
            print(f"   - ID: {admin_existente.user_id}")
            print(f"   - Email: {admin_existente.email}")
            print(f"   - Rol: {admin_existente.rol}")
            print("\n💡 Si olvidaste la contraseña, puedes cambiarla desde el código.")
            return True
        
        # Crear usuario admin
        print("\n🔧 Creando usuario administrador...")
        admin_user = user_manager.crear_usuario(
            username='admin',
            email='admin@proyecto-big-data.com',
            password='admin123',  # ⚠️ CAMBIAR DESPUÉS DEL PRIMER LOGIN
            rol=User.ROLE_ADMIN,
            nombre_completo='Administrador del Sistema'
        )
        
        if admin_user:
            print("✅ Usuario administrador creado exitosamente!")
            print("\n📋 Credenciales de acceso:")
            print("   - Username: admin")
            print("   - Password: admin123")
            print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login!")
            print(f"\n🆔 User ID: {admin_user.user_id}")
            return True
        else:
            print("❌ Error al crear el usuario administrador")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()


def crear_usuarios_ejemplo():
    """Crea usuarios de ejemplo para testing (opcional)."""
    
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB', 'proyecto_big_data')
    
    try:
        client = MongoClient(MONGO_URI)
        user_manager = UserManager(client, MONGO_DB_NAME)
        
        print("\n🔧 Creando usuarios de ejemplo...")
        
        # Usuario Editor
        if not user_manager.obtener_usuario_por_username('editor'):
            editor = user_manager.crear_usuario(
                username='editor',
                email='editor@proyecto-big-data.com',
                password='editor123',
                rol=User.ROLE_EDITOR,
                nombre_completo='Editor de Contenido'
            )
            if editor:
                print("✅ Usuario 'editor' creado (password: editor123)")
        
        # Usuario Viewer
        if not user_manager.obtener_usuario_por_username('viewer'):
            viewer = user_manager.crear_usuario(
                username='viewer',
                email='viewer@proyecto-big-data.com',
                password='viewer123',
                rol=User.ROLE_VIEWER,
                nombre_completo='Usuario Visualizador'
            )
            if viewer:
                print("✅ Usuario 'viewer' creado (password: viewer123)")
        
        print("\n✅ Usuarios de ejemplo creados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al crear usuarios de ejemplo: {e}")
    finally:
        if 'client' in locals():
            client.close()


if __name__ == '__main__':
    print("="*60)
    print("🚀 INICIALIZACIÓN DEL SISTEMA DE USUARIOS")
    print("="*60)
    
    # Crear usuario admin
    success = inicializar_usuario_admin()
    
    if success:
        # Preguntar si crear usuarios de ejemplo
        respuesta = input("\n¿Deseas crear usuarios de ejemplo (editor, viewer)? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'y', 'yes']:
            crear_usuarios_ejemplo()
    
    print("\n" + "="*60)
    print("✅ Inicialización completada")
    print("="*60)
    print("\n💡 Próximos pasos:")
    print("   1. Ejecuta la aplicación: python app.py")
    print("   2. Ve a: http://localhost:5001/login")
    print("   3. Inicia sesión con: admin / admin123")
    print("   4. Cambia la contraseña desde el panel admin")
    print("\n")
