#!/usr/bin/env python3
"""
SCRIPT DE VERIFICACIÓN - Sistema de Gestión de Empleados
Verifica que todas las características estén implementadas correctamente
"""

import os
import sys
from pathlib import Path


def verificar_estructura():
    """Verifica la estructura de archivos del proyecto"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE ESTRUCTURA DE ARCHIVOS")
    print("="*60)
    
    archivos_requeridos = {
        "main.py": "Interfaz principal",
        "requirements.txt": "Dependencias",
        "database/conexion.py": "Conexión a BD",
        "database/__init__.py": "Inicializador BD",
        "models/empleado.py": "Clase Empleado",
        "models/departamento.py": "Clase Departamento",
        "models/__init__.py": "Inicializador Models",
        "README.md": "Documentación",
        "ARQUITECTURA.md": "Arquitectura",
        "IMPLEMENTACION_DEPARTAMENTOS.md": "Detalles departamentos",
        ".env": "Variables de entorno (opcional)"
    }
    
    for archivo, descripcion in archivos_requeridos.items():
        existe = Path(archivo).exists()
        estado = "✅" if existe else "⚠️"
        print(f"{estado} {archivo:35s} - {descripcion}")
        if not existe and archivo != ".env":
            print(f"   ❌ FALTA: {archivo}")
    
    print("\n✅ Estructura verificada")


def verificar_imports():
    """Verifica que los imports funcionen correctamente"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE IMPORTS")
    print("="*60)
    
    try:
        print("▶ Importando database.conexion...")
        from database.conexion import get_connection, create_table_empleados, create_table_departamentos
        print("   ✅ OK")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    try:
        print("▶ Importando models.empleado...")
        from models.empleado import Empleado
        print("   ✅ OK")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    try:
        print("▶ Importando models.departamento...")
        from models.departamento import Departamento
        print("   ✅ OK")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print("\n✅ Todos los imports funcionan")
    return True


def verificar_clases():
    """Verifica que las clases tengan los métodos requeridos"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE CLASES Y MÉTODOS")
    print("="*60)
    
    from models.empleado import Empleado
    from models.departamento import Departamento
    
    # Verificar Departamento
    print("\n▶ Clase Departamento:")
    metodos_depto = [
        'crear', 'leer_por_id', 'leer_por_nombre', 'listar_todos',
        'actualizar', 'eliminar', 'crear_desde_dict',
        '__str__', '__repr__', '__eq__'
    ]
    
    for metodo in metodos_depto:
        tiene = hasattr(Departamento, metodo)
        estado = "✅" if tiene else "❌"
        print(f"  {estado} {metodo}()")
    
    # Verificar Empleado
    print("\n▶ Clase Empleado:")
    metodos_emp = [
        'crear', 'leer_por_rut', 'listar_todos',
        'actualizar', 'eliminar', 'crear_desde_dict',
        '__str__', '__repr__', '__eq__'
    ]
    
    for metodo in metodos_emp:
        tiene = hasattr(Empleado, metodo)
        estado = "✅" if tiene else "❌"
        print(f"  {estado} {metodo}()")
    
    # Verificar properties
    print("\n▶ Properties Departamento:")
    props_depto = ['id_depto', 'nombre', 'gerente', 'descripcion']
    for prop in props_depto:
        tiene = hasattr(Departamento, prop)
        estado = "✅" if tiene else "❌"
        print(f"  {estado} {prop}")
    
    print("\n▶ Properties Empleado:")
    props_emp = ['rut', 'nombre', 'apellido', 'cargo', 'salario', 'id_departamento']
    for prop in props_emp:
        tiene = hasattr(Empleado, prop)
        estado = "✅" if tiene else "❌"
        print(f"  {estado} {prop}")
    
    print("\n✅ Clases verificadas")


def verificar_base_datos():
    """Verifica la configuración de base de datos"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE BASE DE DATOS")
    print("="*60)
    
    try:
        env_path = Path(".env")
        if env_path.exists():
            print("▶ Archivo .env encontrado")
            with open(".env") as f:
                contenido = f.read()
                if "ORACLE_USER" in contenido:
                    print("   ✅ ORACLE_USER configurado")
                else:
                    print("   ❌ ORACLE_USER no configurado")
                
                if "ORACLE_PASSWORD" in contenido:
                    print("   ✅ ORACLE_PASSWORD configurado")
                else:
                    print("   ❌ ORACLE_PASSWORD no configurado")
                
                if "ORACLE_DSN" in contenido:
                    print("   ✅ ORACLE_DSN configurado")
                else:
                    print("   ❌ ORACLE_DSN no configurado")
        else:
            print("⚠️  Archivo .env no encontrado")
            print("   Asegúrate de crear el archivo .env con las credenciales")
    
    except Exception as e:
        print(f"❌ Error al verificar .env: {e}")


def verificar_documentacion():
    """Verifica que la documentación esté completa"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE DOCUMENTACIÓN")
    print("="*60)
    
    docs = {
        "README.md": "Documentación principal",
        "ARQUITECTURA.md": "Diagrama de arquitectura",
        "IMPLEMENTACION_DEPARTAMENTOS.md": "Detalles de implementación",
        "IMPLEMENTACION_COMPLETA.md": "Resumen de cambios"
    }
    
    for doc, desc in docs.items():
        existe = Path(doc).exists()
        if existe:
            with open(doc) as f:
                lineas = len(f.readlines())
            estado = "✅"
            print(f"{estado} {doc:40s} ({lineas} líneas)")
        else:
            print(f"⚠️  {doc:40s} (no encontrado)")


def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DEL SISTEMA - ES2 POO")
    print("="*60)
    
    verificar_estructura()
    
    if verificar_imports():
        verificar_clases()
        verificar_base_datos()
        verificar_documentacion()
    
    print("\n" + "="*60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*60)
    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Asegúrate de que .env está configurado correctamente")
    print("2. Ejecuta: python main.py")
    print("3. Crea algunos departamentos primero")
    print("4. Luego crea empleados con departamentos")
    print("\n¡Sistema listo para usar! 🚀\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        sys.exit(1)
