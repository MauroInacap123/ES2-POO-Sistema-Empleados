"""
Módulo de autenticación y seguridad.
Aquí implementé todo lo relacionado con usuarios, roles, contraseñas hasheadas
y control de acceso basado en roles (RBAC). Este módulo es crítico para la seguridad
del sistema porque valida quién puede hacer qué en la aplicación.
"""

import hashlib
import os
from datetime import datetime
from database.conexion import get_connection
import oracledb


class Autenticacion:
    """Clase para gestionar autenticación y seguridad del sistema."""
    
    ROLES = ["admin", "supervisor", "empleado"]
    
    @staticmethod
    def _hash_password(contraseña):
        """
        Hashea una contraseña usando SHA-256.
        Nunca almaceno contraseñas en texto plano en la BD.
        Esto es un requisito de seguridad fundamental. Si alguien roba la BD,
        las contraseñas siguen siendo seguras porque no se pueden "desencriptar".
        
        Args:
            contraseña (str): Contraseña en texto plano
            
        Returns:
            str: Contraseña hasheada
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()
    
    @staticmethod
    def crear_tabla_usuarios():
        """Crea la tabla de usuarios si no existe."""
        ddl = """
        CREATE TABLE usuarios (
            id_usuario NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre_usuario VARCHAR2(50) NOT NULL UNIQUE,
            contraseña_hash VARCHAR2(64) NOT NULL,
            rol VARCHAR2(20) NOT NULL,
            email VARCHAR2(100),
            activo NUMBER DEFAULT 1,
            fecha_creacion DATE DEFAULT SYSDATE,
            ultimo_login DATE,
            intentos_fallidos NUMBER DEFAULT 0
        )
        """
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Verificar si la tabla ya existe
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM user_tables 
                        WHERE table_name = 'USUARIOS'
                    """)
                    exists = cur.fetchone()[0]
                    
                    if exists:
                        print("[WARN] La tabla 'usuarios' ya existe")
                    else:
                        cur.execute(ddl)
                        print("[OK] Tabla 'usuarios' creada exitosamente")
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al crear tabla usuarios: {e}")
    
    @staticmethod
    def crear_usuario_admin_inicial():
        """Crea un usuario admin inicial si no existen usuarios."""
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Verificar si hay usuarios
                    cur.execute("SELECT COUNT(*) FROM usuarios")
                    count = cur.fetchone()[0]
                    
                    if count == 0:
                        # Crear usuario admin por defecto
                        admin_hash = Autenticacion._hash_password("admin123")
                        cur.execute("""
                            INSERT INTO usuarios 
                            (nombre_usuario, contraseña_hash, rol, email, activo)
                            VALUES ('admin', :hash, 'admin', 'admin@empresa.com', 1)
                        """, {"hash": admin_hash})
                        conn.commit()
                        print("[OK] Usuario admin inicial creado (usuario: admin, contraseña: admin123)")
                        print("  [WARN] IMPORTANTE: Cambia la contraseña del admin al primer login")
        except oracledb.DatabaseError as e:
            print(f"[WARN] Error al crear usuario admin: {e}")
    
    @staticmethod
    def validar_credenciales(nombre_usuario, contraseña):
        """
        Valida las credenciales de un usuario.
        Esta es una de las funciones más críticas de seguridad.
        Comparo el hash de la contraseña ingresada con el hash guardado en la BD.
        Si no coinciden, también incremento el contador de intentos fallidos para
        implementar protección contra fuerza bruta (aunque no la bloqueo automáticamente aquí).
        
        Args:
            nombre_usuario (str): Nombre de usuario
            contraseña (str): Contraseña en texto plano
            
        Returns:
            dict: Datos del usuario si son válidas, None en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    contraseña_hash = Autenticacion._hash_password(contraseña)
                    
                    cur.execute("""
                        SELECT id_usuario, nombre_usuario, rol, email, activo
                        FROM usuarios
                        WHERE nombre_usuario = :usuario AND contraseña_hash = :hash AND activo = 1
                    """, {"usuario": nombre_usuario, "hash": contraseña_hash})
                    
                    row = cur.fetchone()
                    
                    if row:
                        # Resetear intentos fallidos y actualizar último login
                        cur.execute("""
                            UPDATE usuarios
                            SET ultimo_login = SYSDATE, intentos_fallidos = 0
                            WHERE id_usuario = :id
                        """, {"id": row[0]})
                        conn.commit()
                        
                        return {
                            'id_usuario': row[0],
                            'nombre_usuario': row[1],
                            'rol': row[2],
                            'email': row[3]
                        }
                    else:
                        # Incrementar intentos fallidos
                        cur.execute("""
                            UPDATE usuarios
                            SET intentos_fallidos = intentos_fallidos + 1
                            WHERE nombre_usuario = :usuario
                        """, {"usuario": nombre_usuario})
                        conn.commit()
                        
                        return None
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al validar credenciales: {e}")
            return None
    
    @staticmethod
    def cambiar_contraseña(id_usuario, contraseña_actual, contraseña_nueva):
        """
        Cambia la contraseña de un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            contraseña_actual (str): Contraseña actual
            contraseña_nueva (str): Nueva contraseña
            
        Returns:
            bool: True si se cambió exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Verificar contraseña actual
                    hash_actual = Autenticacion._hash_password(contraseña_actual)
                    cur.execute("""
                        SELECT id_usuario FROM usuarios
                        WHERE id_usuario = :id AND contraseña_hash = :hash
                    """, {"id": id_usuario, "hash": hash_actual})
                    
                    if not cur.fetchone():
                        print("[ERROR] Contraseña actual incorrecta")
                        return False
                    
                    # Actualizar contraseña
                    if len(contraseña_nueva) < 6:
                        print("[ERROR] La nueva contraseña debe tener al menos 6 caracteres")
                        return False
                    
                    hash_nueva = Autenticacion._hash_password(contraseña_nueva)
                    cur.execute("""
                        UPDATE usuarios
                        SET contraseña_hash = :hash
                        WHERE id_usuario = :id
                    """, {"hash": hash_nueva, "id": id_usuario})
                    conn.commit()
                    
                    print("[OK] Contraseña cambiada exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al cambiar contraseña: {e}")
            return False
    
    @staticmethod
    def tiene_permiso(rol, accion):
        """
        Verifica si un rol tiene permiso para realizar una acción.
        Aquí implementé el concepto de Control de Acceso Basado en Roles (RBAC).
        Tengo 3 roles: admin (acceso total), supervisor (acceso limitado),
        y empleado (acceso muy restringido). Cada rol tiene una lista de acciones permitidas.
        
        Args:
            rol (str): Rol del usuario
            accion (str): Acción a realizar
            
        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        permisos = {
            'admin': [
                'crear_empleado', 'buscar_empleado', 'listar_empleados', 
                'actualizar_empleado', 'eliminar_empleado',
                'crear_departamento', 'actualizar_departamento', 'eliminar_departamento',
                'crear_proyecto', 'actualizar_proyecto', 'eliminar_proyecto',
                'asignar_empleado_proyecto', 'desasignar_empleado_proyecto',
                'registrar_tiempo', 'actualizar_registro', 'eliminar_registro',
                'generar_informes', 'cambiar_contraseña', 'ver_informes'
            ],
            'supervisor': [
                'buscar_empleado', 'listar_empleados', 
                'registrar_tiempo', 'actualizar_registro',
                'ver_proyectos', 'listar_proyectos',
                'cambiar_contraseña', 'ver_informes'
            ],
            'empleado': [
                'buscar_empleado', 'listar_empleados',
                'registrar_tiempo', 'ver_proyectos',
                'cambiar_contraseña'
            ]
        }
        
        return accion in permisos.get(rol, [])
    
    @staticmethod
    def crear_usuario(nombre_usuario, contraseña, rol, email=None):
        """
        Crea un nuevo usuario.
        
        Args:
            nombre_usuario (str): Nombre de usuario
            contraseña (str): Contraseña
            rol (str): Rol del usuario (admin/supervisor/empleado)
            email (str, optional): Email del usuario
            
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        if len(contraseña) < 6:
            print("[ERROR] La contraseña debe tener al menos 6 caracteres")
            return False
        
        if rol not in Autenticacion.ROLES:
            print(f"[ERROR] Rol inválido. Roles válidos: {', '.join(Autenticacion.ROLES)}")
            return False
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    contraseña_hash = Autenticacion._hash_password(contraseña)
                    cur.execute("""
                        INSERT INTO usuarios 
                        (nombre_usuario, contraseña_hash, rol, email, activo)
                        VALUES (:usuario, :hash, :rol, :email, 1)
                    """, {
                        "usuario": nombre_usuario,
                        "hash": contraseña_hash,
                        "rol": rol,
                        "email": email
                    })
                    conn.commit()
                    print(f"[OK] Usuario '{nombre_usuario}' creado exitosamente con rol '{rol}'")
                    return True
        except oracledb.DatabaseError as e:
            if "UNIQUE constraint" in str(e):
                print(f"[ERROR] El usuario '{nombre_usuario}' ya existe")
            else:
                print(f"[ERROR] Error al crear usuario: {e}")
            return False
    
    @staticmethod
    def listar_usuarios():
        """
        Lista todos los usuarios del sistema.
        
        Returns:
            list: Lista de usuarios
        """
        usuarios = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_usuario, nombre_usuario, rol, email, activo, ultimo_login
                        FROM usuarios
                        ORDER BY nombre_usuario
                    """)
                    for row in cur.fetchall():
                        usuarios.append({
                            'id': row[0],
                            'nombre_usuario': row[1],
                            'rol': row[2],
                            'email': row[3],
                            'activo': row[4],
                            'ultimo_login': row[5]
                        })
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al listar usuarios: {e}")
        
        return usuarios
    
    @staticmethod
    def desactivar_usuario(id_usuario):
        """
        Desactiva un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            bool: True si se desactivó exitosamente
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE usuarios
                        SET activo = 0
                        WHERE id_usuario = :id
                    """, {"id": id_usuario})
                    
                    if cur.rowcount == 0:
                        print("[ERROR] Usuario no encontrado")
                        return False
                    
                    conn.commit()
                    print("[OK] Usuario desactivado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al desactivar usuario: {e}")
            return False


class ControlAcceso:
    """Clase para controlar el acceso a funcionalidades según el rol."""
    
    def __init__(self, usuario_actual=None):
        """
        Inicializa el control de acceso.
        
        Args:
            usuario_actual (dict): Datos del usuario autenticado
        """
        self.usuario_actual = usuario_actual
    
    def verificar_permiso(self, accion):
        """
        Verifica si el usuario actual tiene permiso para la acción.
        
        Args:
            accion (str): Acción a realizar
            
        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        if not self.usuario_actual:
            print("[ERROR] No hay usuario autenticado")
            return False
        
        tiene_permiso = Autenticacion.tiene_permiso(self.usuario_actual['rol'], accion)
        
        if not tiene_permiso:
            print(f"[ERROR] El rol '{self.usuario_actual['rol']}' no tiene permiso para '{accion}'")
        
        return tiene_permiso
    
    def obtener_rol(self):
        """Retorna el rol del usuario actual."""
        return self.usuario_actual['rol'] if self.usuario_actual else None
    
    def obtener_usuario(self):
        """Retorna el nombre del usuario actual."""
        return self.usuario_actual['nombre_usuario'] if self.usuario_actual else None
