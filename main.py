"""
Sistema de Gestión de Empleados - ES2
Asignatura: Programación Orientada a Objetos
Estudiante: Mauricio Bustamante
"""

from database.conexion import create_table_empleados
from models.empleado import Empleado


def mostrar_menu():
    """Muestra el menú principal del sistema."""
    print("\n" + "="*50)
    print("   SISTEMA DE GESTIÓN DE EMPLEADOS")
    print("="*50)
    print("1. Crear nuevo empleado")
    print("2. Buscar empleado por RUT")
    print("3. Listar todos los empleados")
    print("4. Actualizar empleado")
    print("5. Eliminar empleado")
    print("6. Salir")
    print("="*50)


def crear_empleado():
    """Crear un nuevo empleado."""
    print("\n--- CREAR NUEVO EMPLEADO ---")
    try:
        rut = input("RUT (ej: 12.345.678-9): ").strip()
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        cargo = input("Cargo: ").strip()
        salario = float(input("Salario: "))
        departamento = input("Departamento (opcional): ").strip() or None
        
        empleado = Empleado(rut, nombre, apellido, cargo, salario, departamento)
        empleado.crear()
    except ValueError as e:
        print(f"✗ Error de validación: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def buscar_empleado():
    """Buscar empleado por RUT."""
    print("\n--- BUSCAR EMPLEADO ---")
    rut = input("Ingrese RUT a buscar: ").strip()
    empleado = Empleado.leer_por_rut(rut)
    if empleado:
        print(f"\n{empleado}")


def listar_empleados():
    """Listar todos los empleados."""
    print("\n--- LISTADO DE EMPLEADOS ---")
    empleados = Empleado.listar_todos()
    
    if not empleados:
        print("⚠ No hay empleados registrados")
        return
    
    for i, emp in enumerate(empleados, 1):
        print(f"\n{i}. {emp}")


def actualizar_empleado():
    """Actualizar datos de un empleado."""
    print("\n--- ACTUALIZAR EMPLEADO ---")
    rut = input("Ingrese RUT del empleado a actualizar: ").strip()
    
    empleado = Empleado.leer_por_rut(rut)
    if not empleado:
        return
    
    print("\nDeje en blanco para mantener el valor actual")
    try:
        nombre = input(f"Nuevo nombre [{empleado.nombre}]: ").strip()
        if nombre:
            empleado.nombre = nombre
        
        apellido = input(f"Nuevo apellido [{empleado.apellido}]: ").strip()
        if apellido:
            empleado.apellido = apellido
        
        cargo = input(f"Nuevo cargo [{empleado.cargo}]: ").strip()
        if cargo:
            empleado.cargo = cargo
        
        salario_input = input(f"Nuevo salario [{empleado.salario}]: ").strip()
        if salario_input:
            empleado.salario = float(salario_input)
        
        departamento = input(f"Nuevo departamento [{empleado.departamento}]: ").strip()
        if departamento:
            empleado.departamento = departamento
        
        empleado.actualizar()
    except ValueError as e:
        print(f"✗ Error de validación: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def eliminar_empleado():
    """Eliminar un empleado."""
    print("\n--- ELIMINAR EMPLEADO ---")
    rut = input("Ingrese RUT del empleado a eliminar: ").strip()
    
    confirmacion = input(f"¿Está seguro de eliminar al empleado con RUT {rut}? (s/n): ").lower()
    if confirmacion == 's':
        Empleado.eliminar(rut)
    else:
        print("⚠ Operación cancelada")


def main():
    """Función principal del programa."""
    print("\n🚀 Iniciando Sistema de Gestión de Empleados...")
    
    # Crear tabla si no existe
    create_table_empleados()
    
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            crear_empleado()
        elif opcion == '2':
            buscar_empleado()
        elif opcion == '3':
            listar_empleados()
        elif opcion == '4':
            actualizar_empleado()
        elif opcion == '5':
            eliminar_empleado()
        elif opcion == '6':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n✗ Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main()