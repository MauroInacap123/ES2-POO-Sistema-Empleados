from database.conexion import get_connection

# Este modulo es el núcleo de la gestión de empleados. Aquí manejo toda la lógica
# de crear, buscar, actualizar y eliminar empleados en la base de datos.
# Es una clase de negocio (entidad) que implementa el patrón CRUD completo.

class Empleado:
    """
    Clase que representa un empleado y sus operaciones CRUD en la base de datos.
    """
    
    def __init__(self, rut, nombre, apellido, cargo, salario, id_departamento=None):
        self._rut = rut
        self._nombre = nombre
        self._apellido = apellido
        self._cargo = cargo
        self._salario = salario
        self._id_departamento = id_departamento
    
    # ==================== PROPERTIES (Encapsulamiento) ====================
    # Aquí implementé propiedades con @property y setters para encapsular
    # los atributos privados. Esto me permite validar los datos antes de asignarlos
    # y evitar que se asignen valores inválidos directamente desde fuera de la clase.
    # Por ejemplo, el salario no puede ser negativo, y los nombres no pueden estar vacíos.
    
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
    def id_departamento(self):
        return self._id_departamento
    
    @id_departamento.setter
    def id_departamento(self, value):
        self._id_departamento = value
    
    # ==================== MÉTODOS DUNDER ====================
    
    def __str__(self):
        # Este método lo utilizo para obtener una representación legible del empleado
        # cuando hago print(empleado). Devuelve un string con la información más relevante
        # formateada de manera clara para mostrar al usuario en la consola.
        departamento_info = f"Departamento ID: {self.id_departamento}" if self.id_departamento else "Sin departamento"
        return (f"Empleado: {self.nombre} {self.apellido} (RUT: {self.rut}) - "
                f"Cargo: {self.cargo}, Salario: ${self.salario:,.0f}, "
                f"{departamento_info}")
    
    def __repr__(self):
        return (f"Empleado(rut='{self.rut}', nombre='{self.nombre}', "
                f"apellido='{self.apellido}', cargo='{self.cargo}', "
                f"salario={self.salario}, id_departamento={self.id_departamento})")
    
    def __eq__(self, other):
        # Implementé este método para poder comparar dos empleados usando ==
        # Dos empleados son iguales si tienen el mismo RUT (que es único).
        # Esto me permite hacer búsquedas y validaciones fácilmente.
        if not isinstance(other, Empleado):
            return False
        return self.rut == other.rut
    
    # ==================== MÉTODOS CRUD ====================
    
    def crear(self):
        """
        Inserta el empleado actual en la base de datos (CREATE).
        Aquí uso prepared statements con los parámetros nombrados (:rut, :nombre, etc)
        para evitar SQL injection. El try-except me permite capturar errores como
        RUT duplicado o departamento inexistente.
        """
        sql = """
        INSERT INTO empleados (rut, nombre, apellido, cargo, salario, id_departamento)
        VALUES (:rut, :nombre, :apellido, :cargo, :salario, :id_departamento)
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
                        "id_departamento": self.id_departamento
                    })
                    conn.commit()
                    print(f"[OK] Empleado {self.nombre} {self.apellido} creado exitosamente")
        except Exception as e:
            print(f"[ERROR] Error al crear empleado: {e}")
    
    @staticmethod
    def leer_por_rut(rut):
        """
        Busca y retorna un empleado por su RUT (READ).
        Utilizo @staticmethod porque esta búsqueda no depende de una instancia específica.
        Es como un método de clase para recuperar datos de la BD sin necesidad de crear
        un objeto Empleado primero.
        """
        sql = "SELECT * FROM empleados WHERE rut = :rut"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"rut": rut})
                    row = cur.fetchone()
                    
                    if not row:
                        print(f"[WARN] No se encontró empleado con RUT {rut}")
                        return None
                    
                    rut, nombre, apellido, cargo, salario, id_departamento = row
                    empleado = Empleado(rut, nombre, apellido, cargo, salario, id_departamento)
                    print(f"[OK] Empleado encontrado: {empleado}")
                    return empleado
        except Exception as e:
            print(f"[ERROR] Error al leer empleado: {e}")
            return None
    
    @staticmethod
    def listar_todos(limit=100):
        """
        Lista todos los empleados (READ ALL).
        Agregué un LIMIT para evitar que el sistema intente cargar millones de registros
        si la base de datos es muy grande. Por defecto trae 100, pero se puede aumentar.
        """
        sql = f"SELECT * FROM empleados FETCH FIRST {limit} ROWS ONLY"
        empleados = []
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    
                    for row in cur:
                        rut, nombre, apellido, cargo, salario, id_departamento = row
                        empleado = Empleado(rut, nombre, apellido, cargo, salario, id_departamento)
                        empleados.append(empleado)
            
            print(f"[OK] Se encontraron {len(empleados)} empleados")
            return empleados
        except Exception as e:
            print(f"[ERROR] Error al listar empleados: {e}")
            return []
    
    def actualizar(self):
        """
        Actualiza los datos del empleado actual en la base de datos (UPDATE).
        Ejecuta UPDATE solo en la fila donde rut coincide. Si ninguna fila coincide,
        significa que el empleado fue eliminado por otro usuario, así que informo el error.
        """
        sql = """
        UPDATE empleados 
        SET nombre = :nombre, 
            apellido = :apellido, 
            cargo = :cargo, 
            salario = :salario, 
            id_departamento = :id_departamento
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
                        "id_departamento": self.id_departamento
                    })
                    conn.commit()
                    print(f"[OK] Empleado {self.nombre} {self.apellido} actualizado exitosamente")
        except Exception as e:
            print(f"[ERROR] Error al actualizar empleado: {e}")
    
    @staticmethod
    def eliminar(rut):
        """
        Elimina un empleado por su RUT (DELETE).
        Verifico cur.rowcount para confirmar que realmente se eliminó una fila.
        Si rowcount es 0, significa que el RUT no existía en la BD.
        """
        sql = "DELETE FROM empleados WHERE rut = :rut"
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"rut": rut})
                    conn.commit()
                    
                    if cur.rowcount > 0:
                        print(f"[OK] Empleado con RUT {rut} eliminado exitosamente")
                    else:
                        print(f"[WARN] No se encontró empleado con RUT {rut}")
        except Exception as e:
            print(f"[ERROR] Error al eliminar empleado: {e}")
    
    # ==================== MÉTODO DE CLASE ====================
    
    @classmethod
    def crear_desde_dict(cls, data):
        """
        Método de clase para crear un empleado desde un diccionario.
        Ejemplo de uso de @classmethod como fábrica (Factory Pattern).
        Lo uso principalmente cuando leo datos de la BD y necesito convertirlos
        en objetos Empleado. Es más flexible que __init__ porque recibe un diccionario.
        """
        return cls(
            rut=data.get('rut'),
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            cargo=data.get('cargo'),
            salario=data.get('salario'),
            departamento=data.get('departamento')
        )