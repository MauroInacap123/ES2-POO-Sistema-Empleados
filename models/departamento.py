from database.conexion import get_connection


class Departamento:
    """
    Clase que representa un departamento y sus operaciones CRUD en la base de datos.
    """
    
    def __init__(self, nombre, gerente, descripcion=None, id_depto=None):
        self._id_depto = id_depto
        self._nombre = nombre
        self._gerente = gerente
        self._descripcion = descripcion
    
    # ==================== PROPERTIES (Encapsulamiento) ====================
    
    @property
    def id_depto(self):
        return self._id_depto
    
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("El nombre del departamento no puede estar vacío")
        self._nombre = value.strip()
    
    @property
    def gerente(self):
        return self._gerente
    
    @gerente.setter
    def gerente(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("El gerente no puede estar vacío")
        self._gerente = value.strip()
    
    @property
    def descripcion(self):
        return self._descripcion
    
    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = value.strip() if value else None
    
    # ==================== MÉTODOS DUNDER ====================
    
    def __str__(self):
        return (f"Departamento: {self.nombre} (ID: {self.id_depto}) - "
                f"Gerente: {self.gerente}, Descripción: {self.descripcion or 'N/A'}")
    
    def __repr__(self):
        return (f"Departamento(id_depto={self.id_depto}, nombre='{self.nombre}', "
                f"gerente='{self.gerente}', descripcion='{self.descripcion}')")
    
    def __eq__(self, other):
        if not isinstance(other, Departamento):
            return False
        return self.id_depto == other.id_depto
    
    # ==================== MÉTODOS CRUD ====================
    
    def crear(self):
        """
        Inserta el departamento actual en la base de datos (CREATE).
        """
        sql = """
        INSERT INTO departamentos (nombre, gerente, descripcion)
        VALUES (:nombre, :gerente, :descripcion)
        """
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {
                        "nombre": self.nombre,
                        "gerente": self.gerente,
                        "descripcion": self.descripcion
                    })
                    conn.commit()
                    print(f"[OK] Departamento '{self.nombre}' creado exitosamente")
        except Exception as e:
            print(f"[ERROR] Error al crear departamento: {e}")
    
    @staticmethod
    def leer_por_id(id_depto):
        """
        Busca y retorna un departamento por su ID (READ).
        """
        sql = "SELECT id_depto, nombre, gerente, descripcion FROM departamentos WHERE id_depto = :id_depto"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"id_depto": id_depto})
                    row = cur.fetchone()
                    
                    if not row:
                        print(f"[WARN] No se encontró departamento con ID {id_depto}")
                        return None
                    
                    id_d, nombre, gerente, descripcion = row
                    departamento = Departamento(nombre, gerente, descripcion, id_d)
                    print(f"[OK] Departamento encontrado: {departamento}")
                    return departamento
        except Exception as e:
            print(f"[ERROR] Error al leer departamento: {e}")
            return None
    
    @staticmethod
    def leer_por_nombre(nombre):
        """
        Busca y retorna un departamento por su nombre (READ).
        """
        sql = "SELECT id_depto, nombre, gerente, descripcion FROM departamentos WHERE nombre = :nombre"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"nombre": nombre})
                    row = cur.fetchone()
                    
                    if not row:
                        print(f"[WARN] No se encontró departamento con nombre '{nombre}'")
                        return None
                    
                    id_d, nombre_d, gerente, descripcion = row
                    departamento = Departamento(nombre_d, gerente, descripcion, id_d)
                    print(f"[OK] Departamento encontrado: {departamento}")
                    return departamento
        except Exception as e:
            print(f"[ERROR] Error al leer departamento: {e}")
            return None
    
    @staticmethod
    def listar_todos(limit=100):
        """
        Lista todos los departamentos (READ ALL).
        """
        sql = f"SELECT id_depto, nombre, gerente, descripcion FROM departamentos FETCH FIRST {limit} ROWS ONLY"
        departamentos = []
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    
                    for row in cur:
                        id_d, nombre, gerente, descripcion = row
                        departamento = Departamento(nombre, gerente, descripcion, id_d)
                        departamentos.append(departamento)
            
            print(f"[OK] Se encontraron {len(departamentos)} departamentos")
            return departamentos
        except Exception as e:
            print(f"[ERROR] Error al listar departamentos: {e}")
            return []
    
    def actualizar(self):
        """
        Actualiza los datos del departamento actual en la base de datos (UPDATE).
        """
        sql = """
        UPDATE departamentos 
        SET nombre = :nombre, 
            gerente = :gerente, 
            descripcion = :descripcion
        WHERE id_depto = :id_depto
        """
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {
                        "id_depto": self.id_depto,
                        "nombre": self.nombre,
                        "gerente": self.gerente,
                        "descripcion": self.descripcion
                    })
                    conn.commit()
                    print(f"[OK] Departamento '{self.nombre}' actualizado exitosamente")
        except Exception as e:
            print(f"[ERROR] Error al actualizar departamento: {e}")
    
    @staticmethod
    def eliminar(id_depto):
        """
        Elimina un departamento por su ID (DELETE).
        """
        sql = "DELETE FROM departamentos WHERE id_depto = :id_depto"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"id_depto": id_depto})
                    conn.commit()
                    
                    if cur.rowcount > 0:
                        print(f"[OK] Departamento con ID {id_depto} eliminado exitosamente")
                    else:
                        print(f"[WARN] No se encontró departamento con ID {id_depto}")
        except Exception as e:
            print(f"[ERROR] Error al eliminar departamento: {e}")
    
    # ==================== MÉTODO DE CLASE ====================
    
    @classmethod
    def crear_desde_dict(cls, data):
        """
        Método de clase para crear un departamento desde un diccionario.
        Ejemplo de uso de @classmethod como fábrica.
        """
        return cls(
            nombre=data.get('nombre'),
            gerente=data.get('gerente'),
            descripcion=data.get('descripcion'),
            id_depto=data.get('id_depto')
        )
