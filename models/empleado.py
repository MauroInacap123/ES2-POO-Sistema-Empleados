from database.conexion import get_connection


class Empleado:
    """
    Clase que representa un empleado y sus operaciones CRUD en la base de datos.
    """
    
    def __init__(self, rut, nombre, apellido, cargo, salario, departamento=None):
        self._rut = rut
        self._nombre = nombre
        self._apellido = apellido
        self._cargo = cargo
        self._salario = salario
        self._departamento = departamento
    
    # ==================== PROPERTIES (Encapsulamiento) ====================
    
    @property
    def rut(self):
        return self._rut
    
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = value.strip()
    
    @property
    def apellido(self):
        return self._apellido
    
    @apellido.setter
    def apellido(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("El apellido no puede estar vacío")
        self._apellido = value.strip()
    
    @property
    def cargo(self):
        return self._cargo
    
    @cargo.setter
    def cargo(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("El cargo no puede estar vacío")
        self._cargo = value.strip()
    
    @property
    def salario(self):
        return self._salario
    
    @salario.setter
    def salario(self, value):
        if value < 0:
            raise ValueError("El salario no puede ser negativo")
        self._salario = value
    
    @property
    def departamento(self):
        return self._departamento
    
    @departamento.setter
    def departamento(self, value):
        self._departamento = value
    
    # ==================== MÉTODOS DUNDER ====================
    
    def __str__(self):
        return (f"Empleado: {self.nombre} {self.apellido} (RUT: {self.rut}) - "
                f"Cargo: {self.cargo}, Salario: ${self.salario:,.0f}, "
                f"Departamento: {self.departamento or 'N/A'}")
    
    def __repr__(self):
        return (f"Empleado(rut='{self.rut}', nombre='{self.nombre}', "
                f"apellido='{self.apellido}', cargo='{self.cargo}', "
                f"salario={self.salario}, departamento='{self.departamento}')")
    
    def __eq__(self, other):
        if not isinstance(other, Empleado):
            return False
        return self.rut == other.rut
    
    # ==================== MÉTODOS CRUD ====================
    
    def crear(self):
        """
        Inserta el empleado actual en la base de datos (CREATE).
        """
        sql = """
        INSERT INTO empleados (rut, nombre, apellido, cargo, salario, departamento)
        VALUES (:rut, :nombre, :apellido, :cargo, :salario, :departamento)
        """
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {
                        "rut": self.rut,
                        "nombre": self.nombre,
                        "apellido": self.apellido,
                        "cargo": self.cargo,
                        "salario": self.salario,
                        "departamento": self.departamento
                    })
                    conn.commit()
                    print(f"✓ Empleado {self.nombre} {self.apellido} creado exitosamente")
        except Exception as e:
            print(f"✗ Error al crear empleado: {e}")
    
    @staticmethod
    def leer_por_rut(rut):
        """
        Busca y retorna un empleado por su RUT (READ).
        """
        sql = "SELECT * FROM empleados WHERE rut = :rut"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"rut": rut})
                    row = cur.fetchone()
                    
                    if not row:
                        print(f"⚠ No se encontró empleado con RUT {rut}")
                        return None
                    
                    rut, nombre, apellido, cargo, salario, departamento = row
                    empleado = Empleado(rut, nombre, apellido, cargo, salario, departamento)
                    print(f"✓ Empleado encontrado: {empleado}")
                    return empleado
        except Exception as e:
            print(f"✗ Error al leer empleado: {e}")
            return None
    
    @staticmethod
    def listar_todos(limit=100):
        """
        Lista todos los empleados (READ ALL).
        """
        sql = f"SELECT * FROM empleados FETCH FIRST {limit} ROWS ONLY"
        empleados = []
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    
                    for row in cur:
                        rut, nombre, apellido, cargo, salario, departamento = row
                        empleado = Empleado(rut, nombre, apellido, cargo, salario, departamento)
                        empleados.append(empleado)
            
            print(f"✓ Se encontraron {len(empleados)} empleados")
            return empleados
        except Exception as e:
            print(f"✗ Error al listar empleados: {e}")
            return []
    
    def actualizar(self):
        """
        Actualiza los datos del empleado actual en la base de datos (UPDATE).
        """
        sql = """
        UPDATE empleados 
        SET nombre = :nombre, 
            apellido = :apellido, 
            cargo = :cargo, 
            salario = :salario, 
            departamento = :departamento
        WHERE rut = :rut
        """
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {
                        "rut": self.rut,
                        "nombre": self.nombre,
                        "apellido": self.apellido,
                        "cargo": self.cargo,
                        "salario": self.salario,
                        "departamento": self.departamento
                    })
                    conn.commit()
                    print(f"✓ Empleado {self.nombre} {self.apellido} actualizado exitosamente")
        except Exception as e:
            print(f"✗ Error al actualizar empleado: {e}")
    
    @staticmethod
    def eliminar(rut):
        """
        Elimina un empleado por su RUT (DELETE).
        """
        sql = "DELETE FROM empleados WHERE rut = :rut"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"rut": rut})
                    conn.commit()
                    
                    if cur.rowcount > 0:
                        print(f"✓ Empleado con RUT {rut} eliminado exitosamente")
                    else:
                        print(f"⚠ No se encontró empleado con RUT {rut}")
        except Exception as e:
            print(f"✗ Error al eliminar empleado: {e}")
    
    # ==================== MÉTODO DE CLASE ====================
    
    @classmethod
    def crear_desde_dict(cls, data):
        """
        Método de clase para crear un empleado desde un diccionario.
        Ejemplo de uso de @classmethod como fábrica.
        """
        return cls(
            rut=data.get('rut'),
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            cargo=data.get('cargo'),
            salario=data.get('salario'),
            departamento=data.get('departamento')
        )