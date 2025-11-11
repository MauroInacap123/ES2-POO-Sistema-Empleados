import oracledb
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener credenciales desde variables de entorno
username = os.getenv("ORACLE_USER")
dsn = os.getenv("ORACLE_DSN")
password = os.getenv("ORACLE_PASSWORD")


def get_connection():
    """
    Retorna una conexión a la base de datos Oracle.
    """
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        print("✓ Conexión exitosa a Oracle Database")
        return connection
    except oracledb.DatabaseError as e:
        print(f"✗ Error al conectar a la base de datos: {e}")
        raise


def create_table_empleados():
    """
    Crea la tabla 'empleados' en la base de datos si no existe.
    """
    ddl = """
    CREATE TABLE empleados (
        rut VARCHAR2(12) PRIMARY KEY,
        nombre VARCHAR2(100) NOT NULL,
        apellido VARCHAR2(100) NOT NULL,
        cargo VARCHAR2(100) NOT NULL,
        salario NUMBER(10, 2) NOT NULL,
        departamento VARCHAR2(100)
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
                    print("⚠ La tabla 'empleados' ya existe")
                else:
                    cur.execute(ddl)
                    print("✓ Tabla 'empleados' creada exitosamente")
    except oracledb.DatabaseError as e:
        print(f"✗ Error al crear la tabla: {e}")