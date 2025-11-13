import oracledb
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
# Utilizo dotenv para no guardar credenciales sensibles en el código.
# Las credenciales deben estar en un archivo .env que NO se versione en Git.
load_dotenv()

# Obtener credenciales desde variables de entorno
# Esta es la forma segura de manejar datos sensibles en aplicaciones.
username = os.getenv("ORACLE_USER")
dsn = os.getenv("ORACLE_DSN")
password = os.getenv("ORACLE_PASSWORD")


def get_connection():
    """
    Retorna una conexión a la base de datos Oracle.
    Esta es la única función que se debe usar en toda la aplicación para conectarse a la BD.
    Así centralizo toda la lógica de conexión en un solo lugar, lo que facilita
    mantenimiento y cambios futuros (por ejemplo, cambiar de Oracle a PostgreSQL).
    """
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        print("[OK] Conexión exitosa a Oracle Database")
        return connection
    except oracledb.DatabaseError as e:
        print(f"[ERROR] Error al conectar a la base de datos: {e}")
        raise


def create_table_departamentos():
    """
    Crea la tabla 'departamentos' en la base de datos si no existe.
    """
    ddl = """
    CREATE TABLE departamentos (
        id_depto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        nombre VARCHAR2(100) NOT NULL UNIQUE,
        gerente VARCHAR2(100),
        descripcion VARCHAR2(500),
        fecha_creacion DATE DEFAULT SYSDATE
    )
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si la tabla ya existe
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM user_tables 
                    WHERE table_name = 'DEPARTAMENTOS'
                """)
                exists = cur.fetchone()[0]
                
                if exists:
                    print("[WARN] La tabla 'departamentos' ya existe")
                else:
                    cur.execute(ddl)
                    print("[OK] Tabla 'departamentos' creada exitosamente")
    except oracledb.DatabaseError as e:
        print(f"[ERROR] Error al crear la tabla departamentos: {e}")


def create_table_empleados():
    """
    Crea la tabla 'empleados' en la base de datos si no existe.
    Ahora con referencia a departamentos.
    """
    ddl = """
    CREATE TABLE empleados (
        rut VARCHAR2(12) PRIMARY KEY,
        nombre VARCHAR2(100) NOT NULL,
        apellido VARCHAR2(100) NOT NULL,
        cargo VARCHAR2(100) NOT NULL,
        salario NUMBER(10, 2) NOT NULL,
        id_departamento NUMBER,
        CONSTRAINT fk_depto FOREIGN KEY (id_departamento) 
            REFERENCES departamentos(id_depto)
    )
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si la tabla ya existe
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM user_tables 
                    WHERE table_name = 'EMPLEADOS'
                """)
                exists = cur.fetchone()[0]
                
                if exists:
                    print("[WARN] La tabla 'empleados' ya existe")
                else:
                    cur.execute(ddl)
                    print("[OK] Tabla 'empleados' creada exitosamente")
    except oracledb.DatabaseError as e:
        print(f"[ERROR] Error al crear la tabla empleados: {e}")


def create_table_registros_tiempo():
    """
    Crea la tabla 'registros_tiempo' en la base de datos si no existe.
    Registra horas trabajadas por empleados en proyectos.
    """
    ddl = """
    CREATE TABLE registros_tiempo (
        id_registro NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        empleado_rut VARCHAR2(12) NOT NULL,
        fecha_registro DATE NOT NULL,
        horas NUMBER(5, 2) NOT NULL,
        proyecto VARCHAR2(100) NOT NULL,
        descripcion VARCHAR2(500),
        fecha_creacion DATE DEFAULT SYSDATE,
        CONSTRAINT fk_empleado_tiempo FOREIGN KEY (empleado_rut) 
            REFERENCES empleados(rut)
    )
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si la tabla ya existe
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM user_tables 
                    WHERE table_name = 'REGISTROS_TIEMPO'
                """)
                exists = cur.fetchone()[0]
                
                if exists:
                    print("[WARN] La tabla 'registros_tiempo' ya existe")
                else:
                    cur.execute(ddl)
                    print("[OK] Tabla 'registros_tiempo' creada exitosamente")
    except oracledb.DatabaseError as e:
        print(f"[ERROR] Error al crear la tabla registros_tiempo: {e}")


def create_table_proyectos():
    """
    Crea la tabla 'proyectos' en la base de datos si no existe.
    """
    ddl = """
    CREATE TABLE proyectos (
        id_proyecto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        nombre VARCHAR2(100) NOT NULL UNIQUE,
        descripcion VARCHAR2(500),
        fecha_inicio DATE NOT NULL,
        estado VARCHAR2(50) DEFAULT 'Activo',
        fecha_creacion DATE DEFAULT SYSDATE
    )
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si la tabla ya existe
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM user_tables 
                    WHERE table_name = 'PROYECTOS'
                """)
                exists = cur.fetchone()[0]
                
                if exists:
                    print("[WARN] La tabla 'proyectos' ya existe")
                else:
                    cur.execute(ddl)
                    print("[OK] Tabla 'proyectos' creada exitosamente")
    except oracledb.DatabaseError as e:
        print(f"[ERROR] Error al crear la tabla proyectos: {e}")


def create_table_empleado_proyecto():
    """
    Crea la tabla intermedia 'empleado_proyecto' para la relación muchos-a-muchos.
    Esta tabla es esencial para conectar empleados y proyectos.
    Aquí es donde implementé la restricción UNIQUE (empleado_rut, id_proyecto)
    para evitar asignar el mismo empleado al mismo proyecto dos veces.
    """
    ddl = """
    CREATE TABLE empleado_proyecto (
        id_asignacion NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        empleado_rut VARCHAR2(12) NOT NULL,
        id_proyecto NUMBER NOT NULL,
        fecha_asignacion DATE DEFAULT SYSDATE,
        CONSTRAINT fk_emp_proy FOREIGN KEY (empleado_rut) 
            REFERENCES empleados(rut),
        CONSTRAINT fk_proy_emp FOREIGN KEY (id_proyecto) 
            REFERENCES proyectos(id_proyecto),
        CONSTRAINT uk_emp_proy UNIQUE (empleado_rut, id_proyecto)
    )
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si la tabla ya existe
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM user_tables 
                    WHERE table_name = 'EMPLEADO_PROYECTO'
                """)
                exists = cur.fetchone()[0]
                
                if exists:
                    print("[WARN] La tabla 'empleado_proyecto' ya existe")
                else:
                    cur.execute(ddl)
                    print("[OK] Tabla 'empleado_proyecto' creada exitosamente")
    except oracledb.DatabaseError as e:
        print(f"[ERROR] Error al crear la tabla empleado_proyecto: {e}")


def create_table_usuarios():
    """
    Crea la tabla 'usuarios' en la base de datos si no existe.
    Para autenticación y control de acceso.
    """
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
        print(f"[ERROR] Error al crear la tabla usuarios: {e}")