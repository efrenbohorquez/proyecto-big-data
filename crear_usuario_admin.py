# Script de Utilidad para Crear Usuario Administrador
# Uso: python crear_usuario_admin.py

import os

import bcrypt
from dotenv import load_dotenv

from helpers import Mongo_DB

load_dotenv()

def crear_usuario_admin():
    """Crea un usuario administrador en la base de datos"""
    
    print("=" * 70)
    print("CREACIÓN DE USUARIO ADMINISTRADOR")
    print("=" * 70)
    print()
    
    # Conectar a MongoDB
    try:
        mongo_uri = os.getenv('MONGO_URI')
        mongo_db_name = os.getenv('MONGO_DB', 'proyecto_big_data')
        
        if not mongo_uri:
            print("❌ Error: MONGO_URI no configurado en .env")
            return
        
        mongo = Mongo_DB(mongo_uri, mongo_db_name, 'usuarios')
        
        if not mongo.probar_conexion():
            print("❌ Error: No se pudo conectar a MongoDB")
            return
        
        print("✅ Conexión a MongoDB exitosa")
        print()
        
        # Solicitar datos del usuario
        username = input("Ingrese nombre de usuario: ").strip()
        password = input("Ingrese contraseña: ").strip()
        email = input("Ingrese email: ").strip()
        
        if not username or not password:
            print("❌ Error: Usuario y contraseña son obligatorios")
            return
        
        # Hash de la contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Crear documento de usuario
        usuario = {
            'username': username,
            'password': password_hash,
            'email': email,
            'role': 'admin',
            'activo': True,
            'fecha_creacion': None  # Se establecerá en MongoDB
        }
        
        # Insertar en MongoDB
        resultado = mongo.coll.insert_one(usuario)
        
        if resultado.inserted_id:
            print()
            print("=" * 70)
            print("✅ Usuario administrador creado exitosamente")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Role: admin")
            print("=" * 70)
        else:
            print("❌ Error al crear usuario")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    crear_usuario_admin()
