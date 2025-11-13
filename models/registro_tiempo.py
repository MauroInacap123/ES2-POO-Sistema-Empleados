from datetime import datetime
from database.conexion import get_connection
import oracledb

# Este módulo representa los registros de tiempo que cada empleado trabaja.
# Es crítico porque es donde se capturan las horas que trabajó cada empleado en cada proyecto.
# Aquí fijé validaciones importantes: máximo 24 horas por día, mínimo 0.5 horas, etc.

class RegistroTiempo:
    """
    Clase que representa un registro de horas trabajadas por un empleado en un proyecto.
    Gestiona la creación, lectura, actualización y eliminación de registros de tiempo.
    """
    
    def __init__(self, empleado_rut, fecha_registro, horas, proyecto, descripcion=None, id_registro=None):
        """
        Inicializa un objeto RegistroTiempo.
        
        Args:
            empleado_rut (str): RUT del empleado que registra el tiempo
            fecha_registro (datetime): Fecha en que se trabajó
            horas (float): Horas trabajadas (máximo 24)
            proyecto (str): Nombre del proyecto
            descripcion (str, optional): Descripción del trabajo realizado
            id_registro (int, optional): ID del registro (usado al leer de BD)
        """
        self._id_registro = id_registro
        self._empleado_rut = empleado_rut
        self._fecha_registro = fecha_registro
        self._horas = horas
        self._proyecto = proyecto
        self._descripcion = descripcion or ""
        self._fecha_creacion = datetime.now()
    
    @property
    def id_registro(self):
        """Retorna el ID del registro (solo lectura)"""
        return self._id_registro
    
    @property
    def empleado_rut(self):
        """Retorna el RUT del empleado"""
        return self._empleado_rut
    
    @empleado_rut.setter
    def empleado_rut(self, valor):
        """Establece el RUT del empleado"""
        if not valor or not isinstance(valor, str) or len(valor) < 8:
            raise ValueError("El RUT del empleado debe ser válido")
        self._empleado_rut = valor
    
    @property
    def fecha_registro(self):
        """Retorna la fecha del registro"""
        return self._fecha_registro
    
    @fecha_registro.setter
    def fecha_registro(self, valor):
        """Establece la fecha del registro"""
        if isinstance(valor, str):
            try:
                valor = datetime.strptime(valor, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
        if not isinstance(valor, datetime):
            raise ValueError("La fecha debe ser un objeto datetime o string YYYY-MM-DD")
        self._fecha_registro = valor
    
    @property
    def horas(self):
        """Retorna las horas trabajadas"""
        return self._horas
    
    @horas.setter
    def horas(self, valor):
        """Establece las horas trabajadas"""
        try:
            horas_float = float(valor)
            # Aquí valido que las horas estén entre 0.5 y 24
            # No permito valores menores a 0.5 (registro mínimo de media hora)
            # Ni mayores a 24 (un día solo tiene 24 horas)
            if horas_float <= 0 or horas_float > 24:
                raise ValueError("Las horas deben estar entre 0.5 y 24")
            self._horas = horas_float
        except (TypeError, ValueError):
            raise ValueError("Las horas deben ser un número válido entre 0.5 y 24")
    
    @property
    def proyecto(self):
        """Retorna el nombre del proyecto"""
        return self._proyecto
    
    @proyecto.setter
    def proyecto(self, valor):
        """Establece el nombre del proyecto"""
        if not valor or not isinstance(valor, str) or len(valor.strip()) == 0:
            raise ValueError("El nombre del proyecto no puede estar vacío")
        self._proyecto = valor.strip()
    
    @property
    def descripcion(self):
        """Retorna la descripción del trabajo realizado"""
        return self._descripcion
    
    @descripcion.setter
    def descripcion(self, valor):
        """Establece la descripción del trabajo realizado"""
        self._descripcion = (valor or "").strip()
    
    def crear(self):
        """
        Inserta el registro de tiempo en la base de datos.
        
        Aquí ocurre algo importante: primero valido que el empleado exista en la BD
        antes de crear el registro. Esto evita registros huérfanos (registros sin empleado).
        Usos parámetros nombrados único (:p_rut, :p_fecha, etc) porque tuve un error
        ORA-01745 cuando usaba nombres iguales en múltiples queries en el mismo cursor.
        
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Validar que el empleado existe
                    cur.execute("SELECT rut FROM empleados WHERE rut = :rut", 
                               {"rut": self._empleado_rut})
                    if not cur.fetchone():
                        print(f"[ERROR] El empleado con RUT {self._empleado_rut} no existe")
                        return False
                    
                    # Insertar el registro
                    cur.execute("""
                        INSERT INTO registros_tiempo 
                        (empleado_rut, fecha_registro, horas, proyecto, descripcion)
                        VALUES (:p_rut, :p_fecha, :p_horas, :p_proyecto, :p_desc)
                    """, {
                        "p_rut": self._empleado_rut,
                        "p_fecha": self._fecha_registro,
                        "p_horas": self._horas,
                        "p_proyecto": self._proyecto,
                        "p_desc": self._descripcion
                    })
                    conn.commit()
                    print(f"[OK] Registro de tiempo creado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al crear registro de tiempo: {e}")
            return False
    
    @staticmethod
    def leer_por_id(id_registro):
        """
        Busca un registro de tiempo por su ID.
        
        Args:
            id_registro (int): ID del registro a buscar
            
        Returns:
            RegistroTiempo: Objeto con los datos del registro, None si no existe
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_registro, empleado_rut, fecha_registro, horas, 
                               proyecto, descripcion
                        FROM registros_tiempo
                        WHERE id_registro = :id
                    """, {"id": id_registro})
                    row = cur.fetchone()
                    if row:
                        return RegistroTiempo.crear_desde_dict({
                            'id_registro': row[0],
                            'empleado_rut': row[1],
                            'fecha_registro': row[2],
                            'horas': row[3],
                            'proyecto': row[4],
                            'descripcion': row[5]
                        })
                    return None
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al buscar registro: {e}")
            return None
    
    @staticmethod
    def leer_por_empleado(empleado_rut):
        """
        Obtiene todos los registros de tiempo de un empleado.
        Lo uso para ver el historial de horas trabajadas por un empleado específico.
        Ordenados por fecha descendente para ver los más recientes primero.
        
        Args:
            empleado_rut (str): RUT del empleado
            
        Returns:
            list: Lista de objetos RegistroTiempo
        """
        registros = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_registro, empleado_rut, fecha_registro, horas, 
                               proyecto, descripcion
                        FROM registros_tiempo
                        WHERE empleado_rut = :rut
                        ORDER BY fecha_registro DESC
                    """, {"rut": empleado_rut})
                    for row in cur.fetchall():
                        registros.append(RegistroTiempo.crear_desde_dict({
                            'id_registro': row[0],
                            'empleado_rut': row[1],
                            'fecha_registro': row[2],
                            'horas': row[3],
                            'proyecto': row[4],
                            'descripcion': row[5]
                        }))
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al buscar registros del empleado: {e}")
        return registros
    
    @staticmethod
    def leer_por_proyecto(proyecto):
        """
        Obtiene todos los registros de tiempo asociados a un proyecto.
        
        Args:
            proyecto (str): Nombre del proyecto
            
        Returns:
            list: Lista de objetos RegistroTiempo
        """
        registros = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_registro, empleado_rut, fecha_registro, horas, 
                               proyecto, descripcion
                        FROM registros_tiempo
                        WHERE UPPER(proyecto) = UPPER(:proyecto)
                        ORDER BY fecha_registro DESC
                    """, {"proyecto": proyecto})
                    for row in cur.fetchall():
                        registros.append(RegistroTiempo.crear_desde_dict({
                            'id_registro': row[0],
                            'empleado_rut': row[1],
                            'fecha_registro': row[2],
                            'horas': row[3],
                            'proyecto': row[4],
                            'descripcion': row[5]
                        }))
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al buscar registros por proyecto: {e}")
        return registros
    
    @staticmethod
    def listar_todos():
        """
        Obtiene todos los registros de tiempo.
        
        Returns:
            list: Lista de objetos RegistroTiempo
        """
        registros = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_registro, empleado_rut, fecha_registro, horas, 
                               proyecto, descripcion
                        FROM registros_tiempo
                        ORDER BY fecha_registro DESC
                    """)
                    for row in cur.fetchall():
                        registros.append(RegistroTiempo.crear_desde_dict({
                            'id_registro': row[0],
                            'empleado_rut': row[1],
                            'fecha_registro': row[2],
                            'horas': row[3],
                            'proyecto': row[4],
                            'descripcion': row[5]
                        }))
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al listar registros: {e}")
        return registros
    
    def actualizar(self):
        """
        Actualiza el registro de tiempo en la base de datos.
        
        Returns:
            bool: True si se actualizó exitosamente, False en caso contrario
        """
        if not self._id_registro:
            print("[ERROR] No se puede actualizar un registro sin ID")
            return False
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE registros_tiempo
                        SET fecha_registro = :p_fecha,
                            horas = :p_horas,
                            proyecto = :p_proyecto,
                            descripcion = :p_desc
                        WHERE id_registro = :p_id
                    """, {
                        "p_fecha": self._fecha_registro,
                        "p_horas": self._horas,
                        "p_proyecto": self._proyecto,
                        "p_desc": self._descripcion,
                        "p_id": self._id_registro
                    })
                    
                    if cur.rowcount == 0:
                        print(f"[ERROR] No se encontró registro con ID {self._id_registro}")
                        return False
                    
                    conn.commit()
                    print(f"[OK] Registro de tiempo actualizado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al actualizar registro: {e}")
            return False
    
    @staticmethod
    def eliminar(id_registro):
        """
        Elimina un registro de tiempo de la base de datos.
        
        Args:
            id_registro (int): ID del registro a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM registros_tiempo WHERE id_registro = :id", 
                               {"id": id_registro})
                    
                    if cur.rowcount == 0:
                        print(f"[ERROR] No se encontró registro con ID {id_registro}")
                        return False
                    
                    conn.commit()
                    print(f"[OK] Registro de tiempo eliminado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al eliminar registro: {e}")
            return False
    
    @staticmethod
    def crear_desde_dict(data):
        """
        Factory method para crear un objeto RegistroTiempo desde un diccionario.
        Lo uso cuando leo datos de la BD. Es más flexible que usar el constructor
        directamente porque puedo manejar diferentes formatos de fecha que vienen de Oracle.
        
        Args:
            data (dict): Diccionario con los datos del registro
            
        Returns:
            RegistroTiempo: Objeto con los datos del diccionario
        """
        try:
            # Convertir fecha si viene de la BD como objeto datetime
            fecha_registro = data.get('fecha_registro')
            if isinstance(fecha_registro, str):
                fecha_registro = datetime.strptime(fecha_registro, "%Y-%m-%d")
            
            return RegistroTiempo(
                empleado_rut=data.get('empleado_rut'),
                fecha_registro=fecha_registro,
                horas=float(data.get('horas', 0)),
                proyecto=data.get('proyecto'),
                descripcion=data.get('descripcion', ''),
                id_registro=data.get('id_registro')
            )
        except (KeyError, ValueError) as e:
            print(f"[ERROR] Error al crear RegistroTiempo desde diccionario: {e}")
            return None
    
    def __str__(self):
        """Representación legible del registro de tiempo"""
        fecha_str = self._fecha_registro.strftime("%d/%m/%Y")
        return (f"[{self._id_registro}] {self._empleado_rut} - {fecha_str} | "
                f"{self._horas}h | {self._proyecto}")
    
    def __repr__(self):
        """Representación técnica del objeto"""
        return (f"RegistroTiempo(id={self._id_registro}, empleado_rut={self._empleado_rut}, "
                f"fecha={self._fecha_registro}, horas={self._horas}, proyecto={self._proyecto})")
    
    def __eq__(self, otro):
        """Compara dos registros de tiempo por su ID"""
        if not isinstance(otro, RegistroTiempo):
            return False
        return self._id_registro == otro._id_registro
