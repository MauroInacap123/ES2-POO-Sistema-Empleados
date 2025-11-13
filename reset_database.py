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

def reset_tables():
    """Elimina y recrea todas las tablas de la BD: departamentos, empleados, proyectos, empleado_proyecto, registros_tiempo, usuarios"""
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()
        
        # Eliminar tablas en orden correcto (FK primero)
        try:
            cursor.execute("DROP TABLE registros_tiempo")
            print("✓ Tabla 'registros_tiempo' eliminada")
        except Exception as e:
            print(f"⚠ Tabla 'registros_tiempo' no existía o error: {e}")
        
        try:
            cursor.execute("DROP TABLE empleado_proyecto")
            print("✓ Tabla 'empleado_proyecto' eliminada")
        except Exception as e:
            print(f"⚠ Tabla 'empleado_proyecto' no existía o error: {e}")
        
        try:
            cursor.execute("DROP TABLE empleados")
            print("✓ Tabla 'empleados' eliminada")
        except Exception as e:
            print(f"⚠ Tabla 'empleados' no existía o error: {e}")
        
        try:
            cursor.execute("DROP TABLE proyectos")
            print("✓ Tabla 'proyectos' eliminada")
        except Exception as e:
            print(f"⚠ Tabla 'proyectos' no existía o error: {e}")
        
        try:
            cursor.execute("DROP TABLE departamentos")
            print("✓ Tabla 'departamentos' eliminada")
        except Exception as e:
            print(f"⚠ Tabla 'departamentos' no existía o error: {e}")
        
        try:
            cursor.execute("DROP TABLE usuarios")
            print("✓ Tabla 'usuarios' eliminada")
        except Exception as e:
            print(f"⚠ Tabla 'usuarios' no existía o error: {e}")
        
        # Crear tabla departamentos
        ddl_departamentos = """
        CREATE TABLE departamentos (
            id_depto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre VARCHAR2(100) NOT NULL UNIQUE,
            gerente VARCHAR2(100),
            descripcion VARCHAR2(500),
            fecha_creacion DATE DEFAULT SYSDATE
        )
        """
        cursor.execute(ddl_departamentos)
        print("✓ Tabla 'departamentos' creada exitosamente")
        
        # Crear tabla empleados con FK a departamentos
        ddl_empleados = """
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
        cursor.execute(ddl_empleados)
        print("✓ Tabla 'empleados' creada exitosamente")
        
        # Crear tabla proyectos
        ddl_proyectos = """
        CREATE TABLE proyectos (
            id_proyecto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre VARCHAR2(100) NOT NULL UNIQUE,
            descripcion VARCHAR2(500),
            fecha_inicio DATE NOT NULL,
            estado VARCHAR2(50) DEFAULT 'Activo',
            fecha_creacion DATE DEFAULT SYSDATE
        )
        """
        cursor.execute(ddl_proyectos)
        print("✓ Tabla 'proyectos' creada exitosamente")
        
        # Crear tabla intermedia empleado_proyecto
        ddl_empleado_proyecto = """
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
        cursor.execute(ddl_empleado_proyecto)
        print("✓ Tabla 'empleado_proyecto' creada exitosamente")
        
        # Crear tabla registros_tiempo con FK a empleados
        ddl_registros_tiempo = """
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
        cursor.execute(ddl_registros_tiempo)
        print("✓ Tabla 'registros_tiempo' creada exitosamente")
        
        # Crear tabla usuarios
        ddl_usuarios = """
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
        cursor.execute(ddl_usuarios)
        print("✓ Tabla 'usuarios' creada exitosamente")
        
        connection.commit()
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("⚠ ADVERTENCIA: RESET DE BASE DE DATOS")
    print("="*60)
    print("Esto eliminará TODOS los datos de las tablas:")
    print("  - registros_tiempo")
    print("  - empleado_proyecto")
    print("  - empleados")
    print("  - proyectos")
    print("  - departamentos")
    print("  - usuarios")
    print("="*60)
    confirmar = input("¿Desea continuar? (s/n): ")
    if confirmar.lower() == 's':
        reset_tables()
        print("\n✅ Base de datos reseteada exitosamente")
    else:
        print("\nOperación cancelada")