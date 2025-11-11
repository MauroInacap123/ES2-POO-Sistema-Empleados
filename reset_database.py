"""
Script para eliminar y recrear la tabla empleados
"""
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("ORACLE_USER")
dsn = os.getenv("ORACLE_DSN")
password = os.getenv("ORACLE_PASSWORD")

def reset_table():
    """Elimina y recrea la tabla empleados"""
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()
        
        # Eliminar tabla si existe
        try:
            cursor.execute("DROP TABLE empleados")
            print("✓ Tabla 'empleados' eliminada")
        except:
            print("⚠ La tabla no existía")
        
        # Crear tabla nueva
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
        cursor.execute(ddl)
        print("✓ Tabla 'empleados' creada exitosamente")
        
        connection.commit()
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("⚠ ADVERTENCIA: Esto eliminará todos los datos de la tabla empleados")
    confirmar = input("¿Desea continuar? (s/n): ")
    if confirmar.lower() == 's':
        reset_table()
    else:
        print("Operación cancelada")