from datetime import datetime
from database.conexion import get_connection
import oracledb

# Este módulo maneja los proyectos del sistema. Cada proyecto puede tener múltiples empleados
# asignados (relación N:N a través de la tabla empleado_proyecto). Aquí implementé
# la lógica para crear proyectos, asignar empleados, y cambiar estados de proyecto.

class Proyecto:
    """
    Clase que representa un proyecto en el sistema.
    Gestiona la creación, lectura, actualización y eliminación de proyectos.
    También maneja la asignación de empleados a proyectos.
    """
    
    def __init__(self, nombre, descripcion, fecha_inicio, estado="Activo", id_proyecto=None):
        """
        Inicializa un objeto Proyecto.
        
        Args:
            nombre (str): Nombre del proyecto
            descripcion (str): Descripción del proyecto
            fecha_inicio (datetime): Fecha de inicio del proyecto
            estado (str, optional): Estado del proyecto (Activo/Pausado/Finalizado)
            id_proyecto (int, optional): ID del proyecto (usado al leer de BD)
        """
        self._id_proyecto = id_proyecto
        self._nombre = nombre
        self._descripcion = descripcion or ""
        self._fecha_inicio = fecha_inicio
        self._estado = estado
        self._fecha_creacion = datetime.now()
    
    @property
    def id_proyecto(self):
        """Retorna el ID del proyecto (solo lectura)"""
        return self._id_proyecto
    
    @property
    def nombre(self):
        """Retorna el nombre del proyecto"""
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor):
        """Establece el nombre del proyecto"""
        if not valor or not isinstance(valor, str) or len(valor.strip()) == 0:
            raise ValueError("El nombre del proyecto no puede estar vacío")
        self._nombre = valor.strip()
    
    @property
    def descripcion(self):
        """Retorna la descripción del proyecto"""
        return self._descripcion
    
    @descripcion.setter
    def descripcion(self, valor):
        """Establece la descripción del proyecto"""
        self._descripcion = (valor or "").strip()
    
    @property
    def fecha_inicio(self):
        """Retorna la fecha de inicio del proyecto"""
        return self._fecha_inicio
    
    @fecha_inicio.setter
    def fecha_inicio(self, valor):
        """Establece la fecha de inicio del proyecto"""
        if isinstance(valor, str):
            try:
                valor = datetime.strptime(valor, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
        if not isinstance(valor, datetime):
            raise ValueError("La fecha debe ser un objeto datetime o string YYYY-MM-DD")
        self._fecha_inicio = valor
    
    @property
    def estado(self):
        """Retorna el estado del proyecto"""
        return self._estado
    
    @estado.setter
    def estado(self, valor):
        """Establece el estado del proyecto"""
        # Solo permito 3 estados posibles: Activo, Pausado, Finalizado
        # Esto evita que alguien intente crear estados inválidos
        estados_validos = ["Activo", "Pausado", "Finalizado"]
        if valor not in estados_validos:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}")
        self._estado = valor
    
    def crear(self):
        """
        Inserta el proyecto en la base de datos.
        
        Aquí valido que no exista otro proyecto con el mismo nombre (UNIQUE constraint).
        Convierto la fecha de datetime a string para pasarla a Oracle con TO_DATE().
        Cualquier error de BD (nombre duplicado, datos inválidos, etc) lo capturo
        y le informo al usuario qué pasó.
        
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    fecha_str = self._fecha_inicio.strftime("%Y-%m-%d")
                    cur.execute("""
                        INSERT INTO proyectos 
                        (nombre, descripcion, fecha_inicio, estado)
                        VALUES (:p_nombre, :p_desc, TO_DATE(:p_fecha, 'YYYY-MM-DD'), :p_estado)
                    """, {
                        "p_nombre": self._nombre,
                        "p_desc": self._descripcion,
                        "p_fecha": fecha_str,
                        "p_estado": self._estado
                    })
                    conn.commit()
                    print(f"[OK] Proyecto '{self._nombre}' creado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            if "UNIQUE constraint" in str(e):
                print(f"[ERROR] Ya existe un proyecto con el nombre '{self._nombre}'")
            else:
                print(f"[ERROR] Error al crear proyecto: {e}")
            return False
    
    @staticmethod
    def leer_por_id(id_proyecto):
        """
        Busca un proyecto por su ID.
        
        Args:
            id_proyecto (int): ID del proyecto a buscar
            
        Returns:
            Proyecto: Objeto con los datos del proyecto, None si no existe
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_proyecto, nombre, descripcion, fecha_inicio, estado
                        FROM proyectos
                        WHERE id_proyecto = :id
                    """, {"id": id_proyecto})
                    row = cur.fetchone()
                    if row:
                        return Proyecto.crear_desde_dict({
                            'id_proyecto': row[0],
                            'nombre': row[1],
                            'descripcion': row[2],
                            'fecha_inicio': row[3],
                            'estado': row[4]
                        })
                    return None
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al buscar proyecto: {e}")
            return None
    
    @staticmethod
    def leer_por_nombre(nombre):
        """
        Busca un proyecto por su nombre.
        
        Args:
            nombre (str): Nombre del proyecto a buscar
            
        Returns:
            Proyecto: Objeto con los datos del proyecto, None si no existe
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_proyecto, nombre, descripcion, fecha_inicio, estado
                        FROM proyectos
                        WHERE UPPER(nombre) = UPPER(:nombre)
                    """, {"nombre": nombre})
                    row = cur.fetchone()
                    if row:
                        return Proyecto.crear_desde_dict({
                            'id_proyecto': row[0],
                            'nombre': row[1],
                            'descripcion': row[2],
                            'fecha_inicio': row[3],
                            'estado': row[4]
                        })
                    print(f"[ERROR] Proyecto '{nombre}' no encontrado")
                    return None
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al buscar proyecto: {e}")
            return None
    
    @staticmethod
    def listar_todos():
        """
        Obtiene todos los proyectos.
        
        Returns:
            list: Lista de objetos Proyecto
        """
        proyectos = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_proyecto, nombre, descripcion, fecha_inicio, estado
                        FROM proyectos
                        ORDER BY fecha_inicio DESC
                    """)
                    for row in cur.fetchall():
                        proyectos.append(Proyecto.crear_desde_dict({
                            'id_proyecto': row[0],
                            'nombre': row[1],
                            'descripcion': row[2],
                            'fecha_inicio': row[3],
                            'estado': row[4]
                        }))
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al listar proyectos: {e}")
        return proyectos
    
    @staticmethod
    def listar_por_estado(estado):
        """
        Obtiene todos los proyectos con un estado específico.
        
        Args:
            estado (str): Estado del proyecto (Activo/Pausado/Finalizado)
            
        Returns:
            list: Lista de objetos Proyecto
        """
        proyectos = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id_proyecto, nombre, descripcion, fecha_inicio, estado
                        FROM proyectos
                        WHERE estado = :estado
                        ORDER BY fecha_inicio DESC
                    """, {"estado": estado})
                    for row in cur.fetchall():
                        proyectos.append(Proyecto.crear_desde_dict({
                            'id_proyecto': row[0],
                            'nombre': row[1],
                            'descripcion': row[2],
                            'fecha_inicio': row[3],
                            'estado': row[4]
                        }))
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al listar proyectos por estado: {e}")
        return proyectos
    
    def actualizar(self):
        """
        Actualiza el proyecto en la base de datos.
        
        Returns:
            bool: True si se actualizó exitosamente, False en caso contrario
        """
        if not self._id_proyecto:
            print("[ERROR] No se puede actualizar un proyecto sin ID")
            return False
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    fecha_str = self._fecha_inicio.strftime("%Y-%m-%d")
                    cur.execute("""
                        UPDATE proyectos
                        SET nombre = :p_nombre,
                            descripcion = :p_desc,
                            fecha_inicio = TO_DATE(:p_fecha, 'YYYY-MM-DD'),
                            estado = :p_estado
                        WHERE id_proyecto = :p_id
                    """, {
                        "p_nombre": self._nombre,
                        "p_desc": self._descripcion,
                        "p_fecha": fecha_str,
                        "p_estado": self._estado,
                        "p_id": self._id_proyecto
                    })
                    
                    if cur.rowcount == 0:
                        print(f"[ERROR] No se encontró proyecto con ID {self._id_proyecto}")
                        return False
                    
                    conn.commit()
                    print(f"[OK] Proyecto actualizado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            if "UNIQUE constraint" in str(e):
                print(f"[ERROR] Ya existe otro proyecto con el nombre '{self._nombre}'")
            else:
                print(f"[ERROR] Error al actualizar proyecto: {e}")
            return False
    
    @staticmethod
    def eliminar(id_proyecto):
        """
        Elimina un proyecto de la base de datos.
        
        Args:
            id_proyecto (int): ID del proyecto a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Primero, eliminar asignaciones de empleados al proyecto
                    cur.execute("DELETE FROM empleado_proyecto WHERE id_proyecto = :id", 
                               {"id": id_proyecto})
                    
                    # Luego, eliminar el proyecto
                    cur.execute("DELETE FROM proyectos WHERE id_proyecto = :id", 
                               {"id": id_proyecto})
                    
                    if cur.rowcount == 0:
                        print(f"[ERROR] No se encontró proyecto con ID {id_proyecto}")
                        return False
                    
                    conn.commit()
                    print(f"[OK] Proyecto eliminado exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al eliminar proyecto: {e}")
            return False
    
    @staticmethod
    def asignar_empleado(empleado_rut, id_proyecto):
        """
        Asigna un empleado a un proyecto.
        
        Args:
            empleado_rut (str): RUT del empleado
            id_proyecto (int): ID del proyecto
            
        Returns:
            bool: True si se asignó exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Verificar que empleado existe
                    cur.execute("SELECT rut FROM empleados WHERE rut = :rut", 
                               {"rut": empleado_rut})
                    if not cur.fetchone():
                        print(f"[ERROR] Empleado con RUT {empleado_rut} no existe")
                        return False
                    
                    # Verificar que proyecto existe
                    cur.execute("SELECT id_proyecto FROM proyectos WHERE id_proyecto = :id", 
                               {"id": id_proyecto})
                    if not cur.fetchone():
                        print(f"[ERROR] Proyecto con ID {id_proyecto} no existe")
                        return False
                    
                    # Asignar empleado a proyecto
                    cur.execute("""
                        INSERT INTO empleado_proyecto (empleado_rut, id_proyecto)
                        VALUES (:rut, :id)
                    """, {"rut": empleado_rut, "id": id_proyecto})
                    conn.commit()
                    print(f"[OK] Empleado asignado al proyecto exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            if "UNIQUE constraint" in str(e):
                print(f"[ERROR] El empleado ya está asignado a este proyecto")
            else:
                print(f"[ERROR] Error al asignar empleado: {e}")
            return False
    
    @staticmethod
    def desasignar_empleado(empleado_rut, id_proyecto):
        """
        Desasigna un empleado de un proyecto.
        
        Args:
            empleado_rut (str): RUT del empleado
            id_proyecto (int): ID del proyecto
            
        Returns:
            bool: True si se desasignó exitosamente, False en caso contrario
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM empleado_proyecto 
                        WHERE empleado_rut = :rut AND id_proyecto = :id
                    """, {"rut": empleado_rut, "id": id_proyecto})
                    
                    if cur.rowcount == 0:
                        print(f"[ERROR] Asignación no encontrada")
                        return False
                    
                    conn.commit()
                    print(f"[OK] Empleado desasignado del proyecto exitosamente")
                    return True
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al desasignar empleado: {e}")
            return False
    
    @staticmethod
    def obtener_empleados_proyecto(id_proyecto):
        """
        Obtiene todos los empleados asignados a un proyecto.
        
        Args:
            id_proyecto (int): ID del proyecto
            
        Returns:
            list: Lista de RUTs de empleados asignados
        """
        empleados = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT e.rut, e.nombre, e.apellido, e.cargo, e.salario, e.id_departamento
                        FROM empleados e
                        INNER JOIN empleado_proyecto ep ON e.rut = ep.empleado_rut
                        WHERE ep.id_proyecto = :id
                        ORDER BY e.nombre
                    """, {"id": id_proyecto})
                    for row in cur.fetchall():
                        empleados.append({
                            'rut': row[0],
                            'nombre': row[1],
                            'apellido': row[2],
                            'cargo': row[3],
                            'salario': row[4],
                            'id_departamento': row[5]
                        })
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al obtener empleados del proyecto: {e}")
        return empleados
    
    @staticmethod
    def obtener_proyectos_empleado(empleado_rut):
        """
        Obtiene todos los proyectos asignados a un empleado.
        
        Args:
            empleado_rut (str): RUT del empleado
            
        Returns:
            list: Lista de objetos Proyecto
        """
        proyectos = []
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.id_proyecto, p.nombre, p.descripcion, p.fecha_inicio, p.estado
                        FROM proyectos p
                        INNER JOIN empleado_proyecto ep ON p.id_proyecto = ep.id_proyecto
                        WHERE ep.empleado_rut = :rut
                        ORDER BY p.fecha_inicio DESC
                    """, {"rut": empleado_rut})
                    for row in cur.fetchall():
                        proyectos.append(Proyecto.crear_desde_dict({
                            'id_proyecto': row[0],
                            'nombre': row[1],
                            'descripcion': row[2],
                            'fecha_inicio': row[3],
                            'estado': row[4]
                        }))
        except oracledb.DatabaseError as e:
            print(f"[ERROR] Error al obtener proyectos del empleado: {e}")
        return proyectos
    
    @staticmethod
    def crear_desde_dict(data):
        """
        Factory method para crear un objeto Proyecto desde un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del proyecto
            
        Returns:
            Proyecto: Objeto con los datos del diccionario
        """
        try:
            # Convertir fecha si viene de la BD como objeto datetime
            fecha_inicio = data.get('fecha_inicio')
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            
            return Proyecto(
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion', ''),
                fecha_inicio=fecha_inicio,
                estado=data.get('estado', 'Activo'),
                id_proyecto=data.get('id_proyecto')
            )
        except (KeyError, ValueError) as e:
            print(f"[ERROR] Error al crear Proyecto desde diccionario: {e}")
            return None
    
    def __str__(self):
        """Representación legible del proyecto"""
        fecha_str = self._fecha_inicio.strftime("%d/%m/%Y")
        return (f"[{self._id_proyecto}] {self._nombre} | Inicio: {fecha_str} | "
                f"Estado: {self._estado}")
    
    def __repr__(self):
        """Representación técnica del objeto"""
        return (f"Proyecto(id={self._id_proyecto}, nombre={self._nombre}, "
                f"estado={self._estado}, fecha_inicio={self._fecha_inicio})")
    
    def __eq__(self, otro):
        """Compara dos proyectos por su ID"""
        if not isinstance(otro, Proyecto):
            return False
        return self._id_proyecto == otro._id_proyecto
