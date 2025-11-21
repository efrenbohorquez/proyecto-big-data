"""
Modelo de Usuario para el sistema de gestión documental.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import bcrypt


class User:
    """Modelo de usuario con roles y permisos."""
    
    # Roles disponibles
    ROLE_ADMIN = 'admin'
    ROLE_EDITOR = 'editor'
    ROLE_VIEWER = 'viewer'
    
    VALID_ROLES = [ROLE_ADMIN, ROLE_EDITOR, ROLE_VIEWER]
    
    def __init__(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        rol: str = ROLE_VIEWER,
        nombre_completo: str = '',
        activo: bool = True,
        user_id: Optional[int] = None,
        fecha_creacion: Optional[datetime] = None,
        ultima_conexion: Optional[datetime] = None,
        configuracion: Optional[Dict] = None
    ):
        """
        Inicializa un usuario.
        
        Args:
            username: Nombre de usuario único
            email: Email del usuario
            password: Contraseña en texto plano (se hasheará)
            password_hash: Hash de contraseña (si ya está hasheada)
            rol: Rol del usuario (admin, editor, viewer)
            nombre_completo: Nombre completo del usuario
            activo: Si el usuario está activo
            user_id: ID único del usuario
            fecha_creacion: Fecha de creación
            ultima_conexion: Última vez que se conectó
            configuracion: Configuración personalizada
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.rol = rol if rol in self.VALID_ROLES else self.ROLE_VIEWER
        self.nombre_completo = nombre_completo
        self.activo = activo
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.ultima_conexion = ultima_conexion
        self.configuracion = configuracion or {}
        
        # Hashear password si se proporciona
        if password:
            self.password_hash = self._hash_password(password)
        elif password_hash:
            self.password_hash = password_hash
        else:
            raise ValueError("Debe proporcionar password o password_hash")
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hashea una contraseña usando bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash almacenado.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            True si la contraseña es correcta
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def change_password(self, new_password: str) -> None:
        """
        Cambia la contraseña del usuario.
        
        Args:
            new_password: Nueva contraseña en texto plano
        """
        self.password_hash = self._hash_password(new_password)
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico.
        
        Args:
            permission: Nombre del permiso
            
        Returns:
            True si el usuario tiene el permiso
        """
        permissions_by_role = {
            self.ROLE_ADMIN: ['*'],  # Todos los permisos
            self.ROLE_EDITOR: ['read', 'create', 'update', 'search_advanced'],
            self.ROLE_VIEWER: ['read', 'search']
        }
        
        role_permissions = permissions_by_role.get(self.rol, [])
        return '*' in role_permissions or permission in role_permissions
    
    def to_dict(self, include_password_hash: bool = False) -> Dict[str, Any]:
        """
        Convierte el usuario a diccionario.
        
        Args:
            include_password_hash: Si incluir el hash de contraseña
            
        Returns:
            Diccionario con los datos del usuario
        """
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'rol': self.rol,
            'nombre_completo': self.nombre_completo,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultima_conexion': self.ultima_conexion.isoformat() if self.ultima_conexion else None,
            'configuracion': self.configuracion
        }
        
        if include_password_hash:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Crea un usuario desde un diccionario.
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            Instancia de User
        """
        # Convertir fechas de string a datetime si es necesario
        fecha_creacion = data.get('fecha_creacion')
        if isinstance(fecha_creacion, str):
            fecha_creacion = datetime.fromisoformat(fecha_creacion)
        
        ultima_conexion = data.get('ultima_conexion')
        if isinstance(ultima_conexion, str):
            ultima_conexion = datetime.fromisoformat(ultima_conexion)
        
        return cls(
            user_id=data.get('user_id'),
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password_hash'),
            rol=data.get('rol', cls.ROLE_VIEWER),
            nombre_completo=data.get('nombre_completo', ''),
            activo=data.get('activo', True),
            fecha_creacion=fecha_creacion,
            ultima_conexion=ultima_conexion,
            configuracion=data.get('configuracion', {})
        )
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', rol='{self.rol}', activo={self.activo})>"
