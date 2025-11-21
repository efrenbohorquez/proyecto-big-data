"""
Gestor de usuarios para operaciones CRUD en MongoDB.
"""
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserManager:
    """Gestor de usuarios con operaciones CRUD."""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = 'proyecto_big_data'):
        """
        Inicializa el gestor de usuarios.
        
        Args:
            mongo_client: Cliente de MongoDB
            db_name: Nombre de la base de datos
        """
        self.client = mongo_client
        self.db = self.client[db_name]
        self.collection = self.db['usuarios']
        self._crear_indices()
    
    def _crear_indices(self):
        """Crea índices únicos para username y email."""
        try:
            self.collection.create_index('username', unique=True)
            self.collection.create_index('email', unique=True)
            self.collection.create_index('user_id', unique=True)
            logger.info("Índices de usuarios creados exitosamente")
        except Exception as e:
            logger.warning(f"Error al crear índices (pueden ya existir): {e}")
    
    def _get_next_user_id(self) -> int:
        """Obtiene el siguiente ID de usuario disponible."""
        last_user = self.collection.find_one(sort=[('user_id', -1)])
        return (last_user['user_id'] + 1) if last_user and 'user_id' in last_user else 1
    
    def crear_usuario(
        self,
        username: str,
        email: str,
        password: str,
        rol: str = User.ROLE_VIEWER,
        nombre_completo: str = ''
    ) -> Optional[User]:
        """
        Crea un nuevo usuario.
        
        Args:
            username: Nombre de usuario único
            email: Email del usuario
            password: Contraseña en texto plano
            rol: Rol del usuario
            nombre_completo: Nombre completo
            
        Returns:
            Usuario creado o None si hay error
        """
        try:
            # Crear usuario
            user_id = self._get_next_user_id()
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                rol=rol,
                nombre_completo=nombre_completo
            )
            
            # Insertar en MongoDB
            user_dict = user.to_dict(include_password_hash=True)
            self.collection.insert_one(user_dict)
            
            logger.info(f"Usuario '{username}' creado exitosamente con ID {user_id}")
            return user
            
        except DuplicateKeyError as e:
            logger.error(f"Error: Usuario o email ya existe - {e}")
            return None
        except Exception as e:
            logger.error(f"Error al crear usuario: {e}")
            return None
    
    def obtener_usuario(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario o None si no existe
        """
        try:
            user_dict = self.collection.find_one({'user_id': user_id})
            if user_dict:
                user_dict.pop('_id', None)  # Remover ObjectId de MongoDB
                return User.from_dict(user_dict)
            return None
        except Exception as e:
            logger.error(f"Error al obtener usuario {user_id}: {e}")
            return None
    
    def obtener_usuario_por_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su username.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Usuario o None si no existe
        """
        try:
            user_dict = self.collection.find_one({'username': username})
            if user_dict:
                user_dict.pop('_id', None)
                return User.from_dict(user_dict)
            return None
        except Exception as e:
            logger.error(f"Error al obtener usuario '{username}': {e}")
            return None
    
    def actualizar_usuario(
        self,
        user_id: int,
        datos: Dict[str, Any]
    ) -> bool:
        """
        Actualiza los datos de un usuario.
        
        Args:
            user_id: ID del usuario
            datos: Diccionario con los campos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Campos permitidos para actualizar
            campos_permitidos = [
                'email', 'nombre_completo', 'rol', 'activo', 'configuracion'
            ]
            
            # Filtrar solo campos permitidos
            update_data = {k: v for k, v in datos.items() if k in campos_permitidos}
            
            if not update_data:
                logger.warning("No hay datos válidos para actualizar")
                return False
            
            result = self.collection.update_one(
                {'user_id': user_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Usuario {user_id} actualizado exitosamente")
                return True
            else:
                logger.warning(f"Usuario {user_id} no fue modificado")
                return False
                
        except DuplicateKeyError:
            logger.error("Error: Email ya existe")
            return False
        except Exception as e:
            logger.error(f"Error al actualizar usuario {user_id}: {e}")
            return False
    
    def cambiar_password(self, user_id: int, nueva_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            user_id: ID del usuario
            nueva_password: Nueva contraseña en texto plano
            
        Returns:
            True si se cambió correctamente
        """
        try:
            user = self.obtener_usuario(user_id)
            if not user:
                return False
            
            user.change_password(nueva_password)
            
            result = self.collection.update_one(
                {'user_id': user_id},
                {'$set': {'password_hash': user.password_hash}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Contraseña del usuario {user_id} actualizada")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error al cambiar contraseña: {e}")
            return False
    
    def cambiar_rol(self, user_id: int, nuevo_rol: str) -> bool:
        """
        Cambia el rol de un usuario.
        
        Args:
            user_id: ID del usuario
            nuevo_rol: Nuevo rol (admin, editor, viewer)
            
        Returns:
            True si se cambió correctamente
        """
        if nuevo_rol not in User.VALID_ROLES:
            logger.error(f"Rol inválido: {nuevo_rol}")
            return False
        
        return self.actualizar_usuario(user_id, {'rol': nuevo_rol})
    
    def eliminar_usuario(self, user_id: int) -> bool:
        """
        Elimina un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            result = self.collection.delete_one({'user_id': user_id})
            
            if result.deleted_count > 0:
                logger.info(f"Usuario {user_id} eliminado exitosamente")
                return True
            else:
                logger.warning(f"Usuario {user_id} no encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Error al eliminar usuario {user_id}: {e}")
            return False
    
    def listar_usuarios(
        self,
        filtro_rol: Optional[str] = None,
        filtro_activo: Optional[bool] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[User], int]:
        """
        Lista usuarios con filtros y paginación.
        
        Args:
            filtro_rol: Filtrar por rol
            filtro_activo: Filtrar por estado activo
            busqueda: Búsqueda por username o email
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Tupla con (lista de usuarios, total de usuarios)
        """
        try:
            query = {}
            
            if filtro_rol:
                query['rol'] = filtro_rol
            
            if filtro_activo is not None:
                query['activo'] = filtro_activo
            
            if busqueda:
                query['$or'] = [
                    {'username': {'$regex': busqueda, '$options': 'i'}},
                    {'email': {'$regex': busqueda, '$options': 'i'}},
                    {'nombre_completo': {'$regex': busqueda, '$options': 'i'}}
                ]
            
            total = self.collection.count_documents(query)
            cursor = self.collection.find(query).skip(skip).limit(limit).sort('user_id', 1)
            
            usuarios = []
            for user_dict in cursor:
                user_dict.pop('_id', None)
                usuarios.append(User.from_dict(user_dict))
            
            return usuarios, total
            
        except Exception as e:
            logger.error(f"Error al listar usuarios: {e}")
            return [], 0
    
    def verificar_credenciales(self, username: str, password: str) -> Optional[User]:
        """
        Verifica las credenciales de un usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario si las credenciales son correctas, None en caso contrario
        """
        try:
            user = self.obtener_usuario_por_username(username)
            
            if user and user.activo and user.verify_password(password):
                # Actualizar última conexión
                self.collection.update_one(
                    {'user_id': user.user_id},
                    {'$set': {'ultima_conexion': datetime.now()}}
                )
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error al verificar credenciales: {e}")
            return None
    
    def contar_usuarios_por_rol(self) -> Dict[str, int]:
        """
        Cuenta usuarios por rol.
        
        Returns:
            Diccionario con el conteo por rol
        """
        try:
            pipeline = [
                {'$group': {'_id': '$rol', 'count': {'$sum': 1}}}
            ]
            
            result = self.collection.aggregate(pipeline)
            conteo = {item['_id']: item['count'] for item in result}
            
            # Asegurar que todos los roles estén presentes
            for rol in User.VALID_ROLES:
                if rol not in conteo:
                    conteo[rol] = 0
            
            return conteo
            
        except Exception as e:
            logger.error(f"Error al contar usuarios por rol: {e}")
            return {rol: 0 for rol in User.VALID_ROLES}
