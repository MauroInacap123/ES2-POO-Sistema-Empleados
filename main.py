"""
Sistema de Gestión de Empleados - ES2
Asignatura: Programación Orientada a Objetos
Estudiante: Mauricio Bustamante

Este es el archivo principal que ejecuta la aplicación.
Aquí implementé la interfaz de usuario (UI) con menús en consola,
flujo de login, y todas las opciones disponibles para el usuario.
Este es el punto de entrada de la aplicación.
"""

from database.conexion import create_table_empleados, create_table_departamentos, create_table_registros_tiempo, create_table_proyectos, create_table_empleado_proyecto, create_table_usuarios
from models.empleado import Empleado
from models.departamento import Departamento
from models.registro_tiempo import RegistroTiempo
from models.proyecto import Proyecto
from informes import GeneradorInformes
from seguridad import Autenticacion, ControlAcceso
from datetime import datetime


def mostrar_menu():
    """Muestra el menú principal del sistema (DEPRECADO - usar mostrar_menu_principal_autenticado)."""
    print("\n" + "="*50)
    print("   SISTEMA DE GESTIÓN DE EMPLEADOS")
    print("="*50)
    print("1. Crear nuevo empleado")
    print("2. Buscar empleado por RUT")
    print("3. Listar todos los empleados")
    print("4. Actualizar empleado")
    print("5. Reasignar empleado a departamento")
    print("6. Eliminar empleado")
    print("7. Gestionar Departamentos")
    print("8. Registrar Tiempo Trabajado")
    print("9. Gestionar Proyectos")
    print("10. Generar Informes")
    print("11. Salir")
    print("="*50)


def crear_empleado():
    """Crear un nuevo empleado con asignación a departamento."""
    print("\n--- CREAR NUEVO EMPLEADO ---")
    try:
        rut = input("RUT (ej: 12.345.678-9): ").strip()
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        cargo = input("Cargo: ").strip()
        salario = float(input("Salario: "))
        
        # Asignar departamento
        id_departamento = seleccionar_departamento()
        
        empleado = Empleado(rut, nombre, apellido, cargo, salario, id_departamento)
        empleado.crear()
    except ValueError as e:
        print(f"[ERROR] Error de validación: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def seleccionar_departamento():
    """
    Muestra departamentos disponibles y permite seleccionar uno.
    Retorna el ID del departamento o None.
    
    Esta función es importante porque valida que el departamento exista
    antes de asignarlo a un empleado. Así evito crear empleados huérfanos
    (sin departamento válido en la BD).
    """
    print("\n--- Asignar Departamento ---")
    departamentos = Departamento.listar_todos()
    
    if not departamentos:
        print("[WARN] No hay departamentos disponibles")
        return None
    
    print("\nDepartamentos disponibles:")
    for dept in departamentos:
        print(f"  [{dept.id_depto}] {dept.nombre} - Gerente: {dept.gerente}")
    
    while True:
        try:
            id_depto_input = input("\nIngrese ID del departamento (o presione Enter para omitir): ").strip()
            
            if not id_depto_input:
                print("[WARN] Se creará sin departamento asignado")
                return None
            
            id_depto = int(id_depto_input)
            
            # Validar que el departamento existe
            dept = Departamento.leer_por_id(id_depto)
            if dept:
                print(f"[OK] Departamento '{dept.nombre}' seleccionado")
                return id_depto
            else:
                print(f"[ERROR] El departamento con ID {id_depto} no existe")
                print("  Intente de nuevo")
        except ValueError:
            print("[ERROR] ID inválido. Debe ser un número entero")


def buscar_empleado():
    """Buscar empleado por RUT."""
    print("\n--- BUSCAR EMPLEADO ---")
    rut = input("Ingrese RUT a buscar: ").strip()
    empleado = Empleado.leer_por_rut(rut)
    if empleado:
        print(f"\n{empleado}")


def listar_empleados():
    """Listar todos los empleados con información de departamento."""
    print("\n--- LISTADO DE EMPLEADOS ---")
    empleados = Empleado.listar_todos()
    
    if not empleados:
        print("[WARN] No hay empleados registrados")
        return
    
    for i, emp in enumerate(empleados, 1):
        # Obtener nombre del departamento
        dept_info = "Sin departamento"
        if emp.id_departamento:
            dept = Departamento.leer_por_id(emp.id_departamento)
            if dept:
                dept_info = f"{dept.nombre} (ID: {emp.id_departamento})"
        
        print(f"\n{i}. {emp.nombre} {emp.apellido} (RUT: {emp.rut})")
        print(f"   Cargo: {emp.cargo}")
        print(f"   Salario: ${emp.salario:,.0f}")
        print(f"   Departamento: {dept_info}")


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
        
        # Reasignar departamento usando la función
        print(f"\nDepartamento actual: {empleado.id_departamento or 'Ninguno'}")
        reasignar = input("¿Desea cambiar el departamento? (s/n): ").lower()
        if reasignar == 's':
            nuevo_depto = seleccionar_departamento()
            empleado.id_departamento = nuevo_depto
        
        empleado.actualizar()
    except ValueError as e:
        print(f"[ERROR] Error de validación: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def eliminar_empleado():
    """Eliminar un empleado."""
    print("\n--- ELIMINAR EMPLEADO ---")
    rut = input("Ingrese RUT del empleado a eliminar: ").strip()
    
    confirmacion = input(f"¿Está seguro de eliminar al empleado con RUT {rut}? (s/n): ").lower()
    if confirmacion == 's':
        Empleado.eliminar(rut)
    else:
        print("[WARN] Operación cancelada")


def reasignar_empleado_departamento():
    """Reasignar un empleado a un departamento diferente."""
    print("\n--- REASIGNAR EMPLEADO A DEPARTAMENTO ---")
    rut = input("Ingrese RUT del empleado: ").strip()
    
    empleado = Empleado.leer_por_rut(rut)
    if not empleado:
        return
    
    # Mostrar departamento actual
    dept_actual = None
    if empleado.id_departamento:
        dept_actual = Departamento.leer_por_id(empleado.id_departamento)
    
    print(f"\nEmpleado: {empleado.nombre} {empleado.apellido}")
    print(f"Departamento actual: {dept_actual.nombre if dept_actual else 'Ninguno asignado'}")
    
    # Seleccionar nuevo departamento
    nuevo_depto_id = seleccionar_departamento()
    
    if nuevo_depto_id == empleado.id_departamento:
        print("[WARN] El departamento es igual al actual")
        return
    
    # Confirmar reasignación
    if nuevo_depto_id:
        nuevo_dept = Departamento.leer_por_id(nuevo_depto_id)
        print(f"\n[WARN] Se reasignará a: {nuevo_dept.nombre}")
    else:
        print(f"\n[WARN] Se eliminará la asignación de departamento")
    
    confirmar = input("¿Confirmar reasignación? (s/n): ").lower()
    
    if confirmar == 's':
        empleado.id_departamento = nuevo_depto_id
        empleado.actualizar()
        print("[OK] Reasignación completada")
    else:
        print("[WARN] Reasignación cancelada")


# ==================== FUNCIONES DE DEPARTAMENTOS ====================

def mostrar_menu_departamentos():
    """Muestra el menú de gestión de departamentos."""
    print("\n" + "="*50)
    print("   GESTIÓN DE DEPARTAMENTOS")
    print("="*50)
    print("1. Crear nuevo departamento")
    print("2. Buscar departamento por ID")
    print("3. Buscar departamento por nombre")
    print("4. Listar todos los departamentos")
    print("5. Actualizar departamento")
    print("6. Eliminar departamento")
    print("7. Volver al menú principal")
    print("="*50)


def crear_departamento():
    """Crear un nuevo departamento."""
    print("\n--- CREAR NUEVO DEPARTAMENTO ---")
    try:
        nombre = input("Nombre del departamento: ").strip()
        gerente = input("Gerente del departamento: ").strip()
        descripcion = input("Descripción (opcional): ").strip() or None
        
        departamento = Departamento(nombre, gerente, descripcion)
        departamento.crear()
    except ValueError as e:
        print(f"[ERROR] Error de validación: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def buscar_departamento_id():
    """Buscar departamento por ID."""
    print("\n--- BUSCAR DEPARTAMENTO POR ID ---")
    try:
        id_depto = int(input("Ingrese ID del departamento: ").strip())
        departamento = Departamento.leer_por_id(id_depto)
        if departamento:
            print(f"\n{departamento}")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def buscar_departamento_nombre():
    """Buscar departamento por nombre."""
    print("\n--- BUSCAR DEPARTAMENTO POR NOMBRE ---")
    nombre = input("Ingrese nombre del departamento: ").strip()
    departamento = Departamento.leer_por_nombre(nombre)
    if departamento:
        print(f"\n{departamento}")


def listar_departamentos():
    """Listar todos los departamentos."""
    print("\n--- LISTADO DE DEPARTAMENTOS ---")
    departamentos = Departamento.listar_todos()
    
    if not departamentos:
        print("[WARN] No hay departamentos registrados")
        return
    
    for i, dept in enumerate(departamentos, 1):
        print(f"\n{i}. {dept}")


def actualizar_departamento():
    """Actualizar datos de un departamento."""
    print("\n--- ACTUALIZAR DEPARTAMENTO ---")
    try:
        id_depto = int(input("Ingrese ID del departamento a actualizar: ").strip())
        
        departamento = Departamento.leer_por_id(id_depto)
        if not departamento:
            return
        
        print("\nDeje en blanco para mantener el valor actual")
        
        nombre = input(f"Nuevo nombre [{departamento.nombre}]: ").strip()
        if nombre:
            departamento.nombre = nombre
        
        gerente = input(f"Nuevo gerente [{departamento.gerente}]: ").strip()
        if gerente:
            departamento.gerente = gerente
        
        descripcion = input(f"Nueva descripción [{departamento.descripcion or 'Sin descripción'}]: ").strip()
        if descripcion:
            departamento.descripcion = descripcion
        
        departamento.actualizar()
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def eliminar_departamento():
    """Eliminar un departamento."""
    print("\n--- ELIMINAR DEPARTAMENTO ---")
    try:
        id_depto = int(input("Ingrese ID del departamento a eliminar: ").strip())
        
        confirmacion = input(f"¿Está seguro de eliminar el departamento? (s/n): ").lower()
        if confirmacion == 's':
            Departamento.eliminar(id_depto)
        else:
            print("[WARN] Operación cancelada")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def gestionar_departamentos():
    """Menú de gestión de departamentos."""
    while True:
        mostrar_menu_departamentos()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            crear_departamento()
        elif opcion == '2':
            buscar_departamento_id()
        elif opcion == '3':
            buscar_departamento_nombre()
        elif opcion == '4':
            listar_departamentos()
        elif opcion == '5':
            actualizar_departamento()
        elif opcion == '6':
            eliminar_departamento()
        elif opcion == '7':
            print("<- Volviendo al menú principal...")
            break
        else:
            print("\n[ERROR] Opción inválida. Intente nuevamente.")


# ==================== FUNCIONES DE REGISTROS DE TIEMPO ====================

def mostrar_menu_registros_tiempo():
    """Muestra el menú de gestión de registros de tiempo."""
    print("\n" + "="*50)
    print("   REGISTRO DE TIEMPO TRABAJADO")
    print("="*50)
    print("1. Registrar nuevo tiempo")
    print("2. Ver registros de un empleado")
    print("3. Listar todos los registros")
    print("4. Buscar registros por proyecto")
    print("5. Actualizar registro")
    print("6. Eliminar registro")
    print("7. Volver al menú principal")
    print("="*50)


def registrar_tiempo():
    """Registrar horas trabajadas por un empleado."""
    print("\n--- REGISTRAR TIEMPO TRABAJADO ---")
    try:
        empleado_rut = input("RUT del empleado: ").strip()
        
        # Validar que el empleado existe
        empleado = Empleado.leer_por_rut(empleado_rut)
        if not empleado:
            print(f"[ERROR] Empleado con RUT {empleado_rut} no encontrado")
            return
        
        print(f"\n[OK] Empleado: {empleado.nombre} {empleado.apellido}")
        
        # Solicitar fecha
        fecha_str = input("Fecha de trabajo (YYYY-MM-DD): ").strip()
        try:
            fecha_registro = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            print("[ERROR] Formato de fecha inválido. Use YYYY-MM-DD")
            return
        
        # Solicitar horas
        while True:
            try:
                horas = float(input("Horas trabajadas (0.5-24): "))
                if horas <= 0 or horas > 24:
                    print("[ERROR] Las horas deben estar entre 0.5 y 24")
                    continue
                break
            except ValueError:
                print("[ERROR] Ingrese un número válido")
        
        # Solicitar proyecto
        proyecto = input("Nombre del proyecto: ").strip()
        if not proyecto:
            print("[ERROR] El proyecto no puede estar vacío")
            return
        
        # Solicitar descripción (opcional)
        descripcion = input("Descripción del trabajo (opcional): ").strip() or None
        
        # Crear y guardar registro
        registro = RegistroTiempo(
            empleado_rut=empleado_rut,
            fecha_registro=fecha_registro,
            horas=horas,
            proyecto=proyecto,
            descripcion=descripcion
        )
        registro.crear()
        
    except Exception as e:
        print(f"[ERROR] Error al registrar tiempo: {e}")


def buscar_registros_empleado():
    """Buscar todos los registros de un empleado."""
    print("\n--- REGISTROS DE UN EMPLEADO ---")
    empleado_rut = input("RUT del empleado: ").strip()
    
    # Validar que el empleado existe
    empleado = Empleado.leer_por_rut(empleado_rut)
    if not empleado:
        print(f"[ERROR] Empleado con RUT {empleado_rut} no encontrado")
        return
    
    registros = RegistroTiempo.leer_por_empleado(empleado_rut)
    
    if not registros:
        print(f"[WARN] No hay registros de tiempo para {empleado.nombre} {empleado.apellido}")
        return
    
    print(f"\n📋 Registros de {empleado.nombre} {empleado.apellido}:")
    total_horas = 0
    for i, reg in enumerate(registros, 1):
        print(f"\n{i}. {reg}")
        print(f"   Proyecto: {reg.proyecto}")
        if reg.descripcion:
            print(f"   Descripción: {reg.descripcion}")
        total_horas += reg.horas
    
    print(f"\n📊 Total de horas: {total_horas:.1f}h")


def listar_registros_tiempo():
    """Listar todos los registros de tiempo."""
    print("\n--- LISTADO DE REGISTROS DE TIEMPO ---")
    registros = RegistroTiempo.listar_todos()
    
    if not registros:
        print("[WARN] No hay registros de tiempo registrados")
        return
    
    print(f"\n📋 Total de {len(registros)} registros:")
    total_horas = 0
    for i, reg in enumerate(registros, 1):
        empleado = Empleado.leer_por_rut(reg.empleado_rut)
        emp_nombre = f"{empleado.nombre} {empleado.apellido}" if empleado else reg.empleado_rut
        print(f"\n{i}. {reg}")
        print(f"   Empleado: {emp_nombre}")
        print(f"   Proyecto: {reg.proyecto}")
        if reg.descripcion:
            print(f"   Descripción: {reg.descripcion}")
        total_horas += reg.horas
    
    print(f"\n📊 Total de horas registradas: {total_horas:.1f}h")


def buscar_registros_proyecto():
    """Buscar registros de tiempo por proyecto."""
    print("\n--- REGISTROS POR PROYECTO ---")
    proyecto = input("Nombre del proyecto: ").strip()
    
    if not proyecto:
        print("[ERROR] El proyecto no puede estar vacío")
        return
    
    registros = RegistroTiempo.leer_por_proyecto(proyecto)
    
    if not registros:
        print(f"[WARN] No hay registros para el proyecto '{proyecto}'")
        return
    
    print(f"\n📋 Registros del proyecto '{proyecto}':")
    total_horas = 0
    for i, reg in enumerate(registros, 1):
        empleado = Empleado.leer_por_rut(reg.empleado_rut)
        emp_nombre = f"{empleado.nombre} {empleado.apellido}" if empleado else reg.empleado_rut
        print(f"\n{i}. {reg}")
        print(f"   Empleado: {emp_nombre}")
        if reg.descripcion:
            print(f"   Descripción: {reg.descripcion}")
        total_horas += reg.horas
    
    print(f"\n📊 Total de horas en proyecto: {total_horas:.1f}h")


def actualizar_registro_tiempo():
    """Actualizar un registro de tiempo."""
    print("\n--- ACTUALIZAR REGISTRO DE TIEMPO ---")
    try:
        id_registro = int(input("ID del registro a actualizar: "))
        
        registro = RegistroTiempo.leer_por_id(id_registro)
        if not registro:
            print(f"[ERROR] Registro con ID {id_registro} no encontrado")
            return
        
        print(f"\nRegistro actual: {registro}")
        print("Deje en blanco para mantener el valor actual")
        
        # Actualizar fecha
        fecha_str = input(f"Nueva fecha [{registro.fecha_registro.strftime('%Y-%m-%d')}]: ").strip()
        if fecha_str:
            try:
                registro.fecha_registro = datetime.strptime(fecha_str, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Formato de fecha inválido")
                return
        
        # Actualizar horas
        horas_str = input(f"Nuevas horas [{registro.horas}]: ").strip()
        if horas_str:
            try:
                registro.horas = float(horas_str)
            except ValueError:
                print("[ERROR] Valor de horas inválido")
                return
        
        # Actualizar proyecto
        proyecto = input(f"Nuevo proyecto [{registro.proyecto}]: ").strip()
        if proyecto:
            registro.proyecto = proyecto
        
        # Actualizar descripción
        descripcion = input(f"Nueva descripción [{registro.descripcion or 'Sin descripción'}]: ").strip()
        if descripcion:
            registro.descripcion = descripcion
        
        registro.actualizar()
        
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número entero")
    except Exception as e:
        print(f"[ERROR] Error al actualizar registro: {e}")


def eliminar_registro_tiempo():
    """Eliminar un registro de tiempo."""
    print("\n--- ELIMINAR REGISTRO DE TIEMPO ---")
    try:
        id_registro = int(input("ID del registro a eliminar: "))
        
        registro = RegistroTiempo.leer_por_id(id_registro)
        if not registro:
            print(f"[ERROR] Registro con ID {id_registro} no encontrado")
            return
        
        print(f"\nRegistro a eliminar: {registro}")
        confirmacion = input("¿Está seguro de eliminar este registro? (s/n): ").lower()
        
        if confirmacion == 's':
            RegistroTiempo.eliminar(id_registro)
        else:
            print("[WARN] Eliminación cancelada")
            
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número entero")
    except Exception as e:
        print(f"[ERROR] Error al eliminar registro: {e}")


def gestionar_registros_tiempo():
    """Menú de gestión de registros de tiempo."""
    while True:
        mostrar_menu_registros_tiempo()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            registrar_tiempo()
        elif opcion == '2':
            buscar_registros_empleado()
        elif opcion == '3':
            listar_registros_tiempo()
        elif opcion == '4':
            buscar_registros_proyecto()
        elif opcion == '5':
            actualizar_registro_tiempo()
        elif opcion == '6':
            eliminar_registro_tiempo()
        elif opcion == '7':
            print("<- Volviendo al menú principal...")
            break
        else:
            print("\n[ERROR] Opción inválida. Intente nuevamente.")


# ==================== FUNCIONES DE PROYECTOS ====================

def mostrar_menu_proyectos():
    """Muestra el menú de gestión de proyectos."""
    print("\n" + "="*50)
    print("   GESTIÓN DE PROYECTOS")
    print("="*50)
    print("1. Crear nuevo proyecto")
    print("2. Buscar proyecto por ID")
    print("3. Buscar proyecto por nombre")
    print("4. Listar todos los proyectos")
    print("5. Actualizar proyecto")
    print("6. Eliminar proyecto")
    print("7. Asignar empleado a proyecto")
    print("8. Desasignar empleado de proyecto")
    print("9. Ver empleados de un proyecto")
    print("10. Ver proyectos de un empleado")
    print("11. Volver al menú principal")
    print("="*50)


def crear_proyecto():
    """Crear un nuevo proyecto."""
    print("\n--- CREAR NUEVO PROYECTO ---")
    try:
        nombre = input("Nombre del proyecto: ").strip()
        descripcion = input("Descripción (opcional): ").strip() or None
        
        # Solicitar fecha de inicio
        fecha_str = input("Fecha de inicio (YYYY-MM-DD): ").strip()
        try:
            fecha_inicio = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            print("[ERROR] Formato de fecha inválido. Use YYYY-MM-DD")
            return
        
        proyecto = Proyecto(nombre, descripcion, fecha_inicio)
        proyecto.crear()
    except ValueError as e:
        print(f"[ERROR] Error de validación: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def buscar_proyecto_id():
    """Buscar proyecto por ID."""
    print("\n--- BUSCAR PROYECTO POR ID ---")
    try:
        id_proyecto = int(input("Ingrese ID del proyecto: ").strip())
        proyecto = Proyecto.leer_por_id(id_proyecto)
        if proyecto:
            print(f"\n{proyecto}")
            if proyecto.descripcion:
                print(f"Descripción: {proyecto.descripcion}")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def buscar_proyecto_nombre():
    """Buscar proyecto por nombre."""
    print("\n--- BUSCAR PROYECTO POR NOMBRE ---")
    nombre = input("Ingrese nombre del proyecto: ").strip()
    proyecto = Proyecto.leer_por_nombre(nombre)
    if proyecto:
        print(f"\n{proyecto}")
        if proyecto.descripcion:
            print(f"Descripción: {proyecto.descripcion}")


def listar_proyectos():
    """Listar todos los proyectos."""
    print("\n--- LISTADO DE PROYECTOS ---")
    proyectos = Proyecto.listar_todos()
    
    if not proyectos:
        print("[WARN] No hay proyectos registrados")
        return
    
    for i, proy in enumerate(proyectos, 1):
        print(f"\n{i}. {proy}")
        if proy.descripcion:
            print(f"   Descripción: {proy.descripcion}")


def actualizar_proyecto():
    """Actualizar datos de un proyecto."""
    print("\n--- ACTUALIZAR PROYECTO ---")
    try:
        id_proyecto = int(input("Ingrese ID del proyecto a actualizar: ").strip())
        
        proyecto = Proyecto.leer_por_id(id_proyecto)
        if not proyecto:
            return
        
        print("\nDeje en blanco para mantener el valor actual")
        
        nombre = input(f"Nuevo nombre [{proyecto.nombre}]: ").strip()
        if nombre:
            proyecto.nombre = nombre
        
        descripcion = input(f"Nueva descripción [{proyecto.descripcion or 'Sin descripción'}]: ").strip()
        if descripcion:
            proyecto.descripcion = descripcion
        
        fecha_str = input(f"Nueva fecha de inicio [{proyecto.fecha_inicio.strftime('%Y-%m-%d')}]: ").strip()
        if fecha_str:
            try:
                proyecto.fecha_inicio = datetime.strptime(fecha_str, "%Y-%m-%d")
            except ValueError:
                print("[ERROR] Formato de fecha inválido")
                return
        
        print("\nEstados disponibles: Activo, Pausado, Finalizado")
        estado = input(f"Nuevo estado [{proyecto.estado}]: ").strip()
        if estado:
            proyecto.estado = estado
        
        proyecto.actualizar()
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def eliminar_proyecto():
    """Eliminar un proyecto."""
    print("\n--- ELIMINAR PROYECTO ---")
    try:
        id_proyecto = int(input("Ingrese ID del proyecto a eliminar: ").strip())
        
        proyecto = Proyecto.leer_por_id(id_proyecto)
        if not proyecto:
            return
        
        confirmacion = input(f"¿Está seguro de eliminar '{proyecto.nombre}'? (s/n): ").lower()
        if confirmacion == 's':
            Proyecto.eliminar(id_proyecto)
        else:
            print("[WARN] Operación cancelada")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def asignar_empleado_proyecto():
    """Asignar un empleado a un proyecto."""
    print("\n--- ASIGNAR EMPLEADO A PROYECTO ---")
    
    empleado_rut = input("RUT del empleado: ").strip()
    
    # Validar que el empleado existe
    empleado = Empleado.leer_por_rut(empleado_rut)
    if not empleado:
        print(f"[ERROR] Empleado con RUT {empleado_rut} no encontrado")
        return
    
    print(f"[OK] Empleado: {empleado.nombre} {empleado.apellido}")
    
    # Listar proyectos disponibles
    proyectos = Proyecto.listar_todos()
    
    if not proyectos:
        print("[WARN] No hay proyectos disponibles")
        return
    
    print("\nProyectos disponibles:")
    for proy in proyectos:
        print(f"  [{proy.id_proyecto}] {proy.nombre} ({proy.estado})")
    
    try:
        id_proyecto = int(input("\nIngrese ID del proyecto: "))
        
        # Verificar que el proyecto existe
        proyecto = Proyecto.leer_por_id(id_proyecto)
        if not proyecto:
            print(f"[ERROR] Proyecto con ID {id_proyecto} no existe")
            return
        
        # Asignar empleado
        if Proyecto.asignar_empleado(empleado_rut, id_proyecto):
            print(f"[OK] {empleado.nombre} asignado a '{proyecto.nombre}'")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")


def desasignar_empleado_proyecto():
    """Desasignar un empleado de un proyecto."""
    print("\n--- DESASIGNAR EMPLEADO DE PROYECTO ---")
    
    empleado_rut = input("RUT del empleado: ").strip()
    
    # Validar que el empleado existe
    empleado = Empleado.leer_por_rut(empleado_rut)
    if not empleado:
        print(f"[ERROR] Empleado con RUT {empleado_rut} no encontrado")
        return
    
    print(f"[OK] Empleado: {empleado.nombre} {empleado.apellido}")
    
    # Obtener proyectos del empleado
    proyectos = Proyecto.obtener_proyectos_empleado(empleado_rut)
    
    if not proyectos:
        print("[WARN] El empleado no está asignado a ningún proyecto")
        return
    
    print("\nProyectos asignados:")
    for proy in proyectos:
        print(f"  [{proy.id_proyecto}] {proy.nombre}")
    
    try:
        id_proyecto = int(input("\nIngrese ID del proyecto para desasignar: "))
        
        if Proyecto.desasignar_empleado(empleado_rut, id_proyecto):
            proyecto = Proyecto.leer_por_id(id_proyecto)
            print(f"[OK] {empleado.nombre} desasignado de '{proyecto.nombre}'")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")


def ver_empleados_proyecto():
    """Ver todos los empleados asignados a un proyecto."""
    print("\n--- EMPLEADOS DE UN PROYECTO ---")
    
    try:
        id_proyecto = int(input("Ingrese ID del proyecto: ").strip())
        
        proyecto = Proyecto.leer_por_id(id_proyecto)
        if not proyecto:
            print(f"[ERROR] Proyecto con ID {id_proyecto} no encontrado")
            return
        
        empleados = Proyecto.obtener_empleados_proyecto(id_proyecto)
        
        if not empleados:
            print(f"[WARN] El proyecto '{proyecto.nombre}' no tiene empleados asignados")
            return
        
        print(f"\n📋 Empleados asignados a '{proyecto.nombre}':")
        for i, emp in enumerate(empleados, 1):
            dept = Departamento.leer_por_id(emp['id_departamento']) if emp['id_departamento'] else None
            dept_info = f" ({dept.nombre})" if dept else ""
            print(f"\n{i}. {emp['nombre']} {emp['apellido']} (RUT: {emp['rut']})")
            print(f"   Cargo: {emp['cargo']}")
            print(f"   Salario: ${emp['salario']:,.0f}")
            if emp['id_departamento']:
                print(f"   Departamento: {dept_info}")
    except ValueError:
        print("[ERROR] ID inválido. Debe ser un número.")


def ver_proyectos_empleado():
    """Ver todos los proyectos asignados a un empleado."""
    print("\n--- PROYECTOS DE UN EMPLEADO ---")
    
    empleado_rut = input("Ingrese RUT del empleado: ").strip()
    
    empleado = Empleado.leer_por_rut(empleado_rut)
    if not empleado:
        print(f"[ERROR] Empleado con RUT {empleado_rut} no encontrado")
        return
    
    proyectos = Proyecto.obtener_proyectos_empleado(empleado_rut)
    
    if not proyectos:
        print(f"[WARN] {empleado.nombre} {empleado.apellido} no está asignado a ningún proyecto")
        return
    
    print(f"\n📋 Proyectos de {empleado.nombre} {empleado.apellido}:")
    for i, proy in enumerate(proyectos, 1):
        print(f"\n{i}. {proy}")
        if proy.descripcion:
            print(f"   Descripción: {proy.descripcion}")


def gestionar_proyectos():
    """Menú de gestión de proyectos."""
    while True:
        mostrar_menu_proyectos()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            crear_proyecto()
        elif opcion == '2':
            buscar_proyecto_id()
        elif opcion == '3':
            buscar_proyecto_nombre()
        elif opcion == '4':
            listar_proyectos()
        elif opcion == '5':
            actualizar_proyecto()
        elif opcion == '6':
            eliminar_proyecto()
        elif opcion == '7':
            asignar_empleado_proyecto()
        elif opcion == '8':
            desasignar_empleado_proyecto()
        elif opcion == '9':
            ver_empleados_proyecto()
        elif opcion == '10':
            ver_proyectos_empleado()
        elif opcion == '11':
            print("<- Volviendo al menú principal...")
            break
        else:
            print("\n[ERROR] Opción inválida. Intente nuevamente.")


# ==================== FUNCIONES DE INFORMES ====================

def mostrar_menu_informes():
    """Muestra el menú de generación de informes."""
    print("\n" + "="*50)
    print("   GENERACIÓN DE INFORMES")
    print("="*50)
    print("1. Informe de empleados")
    print("2. Informe de departamentos")
    print("3. Informe de proyectos")
    print("4. Informe de registros de tiempo")
    print("5. Informe de asignaciones empleado-proyecto")
    print("6. Generar TODOS los informes (CSV)")
    print("7. Cambiar contraseña")
    print("8. Volver al menú principal")
    print("="*50)


def generar_informes():
    """Menú para generar informes."""
    generador = GeneradorInformes()
    
    while True:
        mostrar_menu_informes()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            generador.informe_empleados(mostrar=True, exportar=False)
        elif opcion == '2':
            generador.informe_departamentos(mostrar=True, exportar=False)
        elif opcion == '3':
            generador.informe_proyectos(mostrar=True, exportar=False)
        elif opcion == '4':
            generador.informe_registros_tiempo(mostrar=True, exportar=False)
        elif opcion == '5':
            generador.informe_asignaciones_empleado_proyecto(mostrar=True, exportar=False)
        elif opcion == '6':
            generador.generar_todos_informes_csv()
        elif opcion == '7':
            cambiar_contraseña_usuario()
        elif opcion == '8':
            print("<- Volviendo al menú principal...")
            break
        else:
            print("\n[ERROR] Opción inválida. Intente nuevamente.")


def cambiar_contraseña_usuario():
    """Permite al usuario cambiar su contraseña."""
    print("\n--- CAMBIAR CONTRASEÑA ---")
    contraseña_actual = input("Contraseña actual: ")
    contraseña_nueva = input("Nueva contraseña (mín. 6 caracteres): ")
    contraseña_confirmar = input("Confirmar nueva contraseña: ")
    
    if contraseña_nueva != contraseña_confirmar:
        print("[ERROR] Las contraseñas no coinciden")
        return
    
    if len(contraseña_nueva) < 6:
        print("[ERROR] La contraseña debe tener al menos 6 caracteres")
        return


# ==================== FUNCIONES DE AUTENTICACIÓN ====================

def pantalla_login():
    """
    Pantalla de login del sistema.
    
    Returns:
        dict: Datos del usuario autenticado, None si cancela
    """
    print("\n" + "="*50)
    print("   SISTEMA DE GESTIÓN DE EMPLEADOS")
    print("   AUTENTICACIÓN".center(50))
    print("="*50)
    
    max_intentos = 3
    intento = 0
    
    while intento < max_intentos:
        print(f"\nIntento {intento + 1} de {max_intentos}")
        nombre_usuario = input("Usuario: ").strip()
        contraseña = input("Contraseña: ")
        
        usuario = Autenticacion.validar_credenciales(nombre_usuario, contraseña)
        
        if usuario:
            print(f"\n[OK] Bienvenido, {usuario['nombre_usuario']}!")
            return usuario
        else:
            intento += 1
            if intento < max_intentos:
                print(f"[ERROR] Credenciales inválidas. Intente de nuevo.")
            else:
                print(f"[ERROR] Ha excedido el número máximo de intentos.")
                return None
    
    return None


def mostrar_menu_principal_autenticado(usuario):
    """Muestra el menú principal adaptado al rol del usuario."""
    rol = usuario['rol'].upper()
    print("\n" + "="*50)
    print("   SISTEMA DE GESTIÓN DE EMPLEADOS")
    print(f"   Usuario: {usuario['nombre_usuario']} ({rol})")
    print("="*50)
    print("1. Crear nuevo empleado")
    print("2. Buscar empleado por RUT")
    print("3. Listar todos los empleados")
    print("4. Actualizar empleado")
    print("5. Reasignar empleado a departamento")
    print("6. Eliminar empleado")
    print("7. Gestionar Departamentos")
    print("8. Registrar Tiempo Trabajado")
    print("9. Gestionar Proyectos")
    print("10. Generar Informes")
    print("11. Salir")
    print("="*50)


def main():
    """Función principal del programa."""
    print("\n🚀 Iniciando Sistema de Gestión de Empleados...")
    
    # Crear tablas si no existen
    create_table_departamentos()
    create_table_empleados()
    create_table_proyectos()
    create_table_empleado_proyecto()
    create_table_registros_tiempo()
    create_table_usuarios()
    
    # Crear usuario admin inicial si no existen usuarios
    Autenticacion.crear_usuario_admin_inicial()
    
    # Autenticarse
    usuario = pantalla_login()
    
    if not usuario:
        print("\n[ERROR] No se pudo autenticar. El programa se cerrará.")
        return
    
    # Control de acceso
    control = ControlAcceso(usuario)
    
    while True:
        mostrar_menu_principal_autenticado(usuario)
        opcion = input("\nSeleccione una opción: ").strip()
        
        # Verificar permisos según la opción
        if opcion == '1' and not control.verificar_permiso('crear_empleado'):
            continue
        elif opcion == '6' and not control.verificar_permiso('eliminar_empleado'):
            continue
        elif opcion == '10' and not control.verificar_permiso('ver_informes'):
            continue
        
        if opcion == '1':
            crear_empleado()
        elif opcion == '2':
            buscar_empleado()
        elif opcion == '3':
            listar_empleados()
        elif opcion == '4':
            actualizar_empleado()

        elif opcion == '5':
            reasignar_empleado_departamento()
        elif opcion == '6':
            eliminar_empleado()
        elif opcion == '7':
            gestionar_departamentos()
        elif opcion == '8':
            gestionar_registros_tiempo()
        elif opcion == '9':
            gestionar_proyectos()
        elif opcion == '10':
            generar_informes()
        elif opcion == '11':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n[ERROR] Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main()