#!/usr/bin/env python3
"""
EJEMPLOS DE USO - Sistema de Gestión de Empleados
Demuestra cómo usar las clases Empleado y Departamento directamente
"""

from models.empleado import Empleado
from models.departamento import Departamento
from database.conexion import create_table_departamentos, create_table_empleados


def ejemplo_crear_departamentos():
    """Ejemplo: Crear departamentos"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Crear Departamentos")
    print("="*60)
    
    # Crear departamento 1
    dept_it = Departamento(
        nombre="Tecnología",
        gerente="Carlos López",
        descripcion="Departamento de Infraestructura y Desarrollo"
    )
    dept_it.crear()
    
    # Crear departamento 2
    dept_rh = Departamento(
        nombre="Recursos Humanos",
        gerente="María González",
        descripcion="Departamento de RRHH y Nómina"
    )
    dept_rh.crear()
    
    # Crear departamento 3
    dept_ven = Departamento(
        nombre="Ventas",
        gerente="Juan Pérez",
        descripcion="Departamento Comercial"
    )
    dept_ven.crear()


def ejemplo_crear_empleados():
    """Ejemplo: Crear empleados con relación a departamentos"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Crear Empleados con Departamentos")
    print("="*60)
    
    # Primero obtener IDs de departamentos (en producción, los usuarios los seleccionan)
    depts = Departamento.listar_todos()
    
    if len(depts) >= 2:
        dept_it = depts[0]
        dept_rh = depts[1]
        
        # Crear empleados
        emp1 = Empleado(
            rut="12.345.678-9",
            nombre="Pedro",
            apellido="García",
            cargo="Desarrollador Python",
            salario=3500000,
            id_departamento=dept_it.id_depto
        )
        emp1.crear()
        
        emp2 = Empleado(
            rut="11.222.333-4",
            nombre="Laura",
            apellido="Martínez",
            cargo="Especialista en Nómina",
            salario=2800000,
            id_departamento=dept_rh.id_depto
        )
        emp2.crear()
        
        emp3 = Empleado(
            rut="22.333.444-5",
            nombre="Miguel",
            apellido="Rodríguez",
            cargo="Ingeniero DevOps",
            salario=4200000,
            id_departamento=dept_it.id_depto
        )
        emp3.crear()


def ejemplo_buscar_departamento():
    """Ejemplo: Buscar departamentos por ID y nombre"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Buscar Departamentos")
    print("="*60)
    
    # Buscar por ID
    print("\n▶ Búsqueda por ID:")
    dept = Departamento.leer_por_id(1)
    
    # Buscar por nombre
    print("\n▶ Búsqueda por nombre:")
    dept = Departamento.leer_por_nombre("Tecnología")


def ejemplo_listar_departamentos():
    """Ejemplo: Listar todos los departamentos"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Listar Departamentos")
    print("="*60)
    
    depts = Departamento.listar_todos()
    print(f"\n📋 Total de departamentos: {len(depts)}\n")
    
    for i, dept in enumerate(depts, 1):
        print(f"{i}. {dept}")


def ejemplo_actualizar_departamento():
    """Ejemplo: Actualizar un departamento"""
    print("\n" + "="*60)
    print("EJEMPLO 5: Actualizar Departamento")
    print("="*60)
    
    # Obtener departamento
    dept = Departamento.leer_por_id(1)
    
    if dept:
        print(f"\n▶ Antes: {dept}")
        
        # Actualizar datos
        dept.nombre = "Tecnología e Infraestructura"
        dept.gerente = "Carlos López Silva"
        dept.descripcion = "Desarrollo, infraestructura y soporte técnico"
        
        dept.actualizar()
        
        print(f"\n▶ Después: {dept}")


def ejemplo_buscar_empleado():
    """Ejemplo: Buscar empleado por RUT"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Buscar Empleado")
    print("="*60)
    
    emp = Empleado.leer_por_rut("12.345.678-9")
    # Nota: Muestra ID de departamento, no el nombre
    # Para mostrar el nombre, harías:
    if emp and emp.id_departamento:
        dept = Departamento.leer_por_id(emp.id_departamento)
        if dept:
            print(f"\n  Departamento del empleado: {dept.nombre}")


def ejemplo_listar_empleados():
    """Ejemplo: Listar todos los empleados"""
    print("\n" + "="*60)
    print("EJEMPLO 7: Listar Empleados")
    print("="*60)
    
    emps = Empleado.listar_todos()
    print(f"\n📋 Total de empleados: {len(emps)}\n")
    
    for i, emp in enumerate(emps, 1):
        dept_info = ""
        if emp.id_departamento:
            dept = Departamento.leer_por_id(emp.id_departamento)
            if dept:
                dept_info = f" | Departamento: {dept.nombre}"
        
        print(f"{i}. {emp}{dept_info}")


def ejemplo_actualizar_empleado():
    """Ejemplo: Actualizar un empleado"""
    print("\n" + "="*60)
    print("EJEMPLO 8: Actualizar Empleado")
    print("="*60)
    
    emp = Empleado.leer_por_rut("12.345.678-9")
    
    if emp:
        print(f"\n▶ Antes: {emp}")
        
        # Actualizar datos
        emp.cargo = "Senior Python Developer"
        emp.salario = 4500000
        
        # Cambiar departamento (obtener nuevo ID)
        depts = Departamento.listar_todos()
        if len(depts) > 1:
            emp.id_departamento = depts[1].id_depto
        
        emp.actualizar()
        
        print(f"\n▶ Después: {emp}")


def ejemplo_crear_desde_dict():
    """Ejemplo: Usar factory pattern para crear objetos desde diccionarios"""
    print("\n" + "="*60)
    print("EJEMPLO 9: Factory Pattern (crear_desde_dict)")
    print("="*60)
    
    # Crear departamento desde diccionario
    data_dept = {
        'nombre': 'Marketing',
        'gerente': 'Sandra Acuña',
        'descripcion': 'Departamento de Marketing y Publicidad'
    }
    
    dept = Departamento.crear_desde_dict(data_dept)
    print(f"\n▶ Departamento creado: {dept}")
    
    # Crear empleado desde diccionario
    data_emp = {
        'rut': '33.444.555-6',
        'nombre': 'Fernando',
        'apellido': 'López',
        'cargo': 'Especialista en Marketing Digital',
        'salario': 3200000,
        'id_departamento': None  # Se asignaría después de obtener el ID real
    }
    
    emp = Empleado.crear_desde_dict(data_emp)
    print(f"▶ Empleado creado: {emp}")


def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "="*60)
    print("🚀 DEMOSTRACIONES - Sistema de Gestión de Empleados")
    print("="*60)
    
    # Inicializar BD
    print("\n▶ Inicializando base de datos...")
    create_table_departamentos()
    create_table_empleados()
    
    # Ejecutar ejemplos
    ejemplo_crear_departamentos()
    ejemplo_crear_empleados()
    ejemplo_buscar_departamento()
    ejemplo_listar_departamentos()
    ejemplo_actualizar_departamento()
    ejemplo_buscar_empleado()
    ejemplo_listar_empleados()
    ejemplo_actualizar_empleado()
    ejemplo_crear_desde_dict()
    
    print("\n" + "="*60)
    print("✅ Demostraciones completadas")
    print("="*60)


if __name__ == "__main__":
    # Descomenta la línea siguiente para ejecutar los ejemplos
    # main()
    
    print("\n⚠️  NOTA: Los ejemplos están comentados por defecto.")
    print("   Descomenta 'main()' en la última línea para ejecutarlos.")
    print("\n   Alternativamente, usa: python main.py")
    print("   para acceder al menú interactivo del sistema.")
