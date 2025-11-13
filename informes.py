"""
Módulo de generación de informes y exportación de datos.
Aquí implementé 6 tipos de informes diferentes que permiten generar reportes
de empleados, departamentos, proyectos y registros de tiempo.
Todos los informes se exportan a CSV para que se puedan abrir en Excel y manipular fácilmente.
Este módulo es esencial para que el administrador pueda analizar los datos del sistema.
"""

import csv
import os
from datetime import datetime
from models.empleado import Empleado
from models.departamento import Departamento
from models.proyecto import Proyecto
from models.registro_tiempo import RegistroTiempo


class GeneradorInformes:
    """
    Clase para generar informes y exportar datos.
    Aquí centralicé toda la lógica de generación de reportes.
    Cada informe puede mostrarse en consola o exportarse a CSV.
    Uso timestamps en los nombres de archivo para que no se sobrescriban los informes antiguos.
    """
    
    def __init__(self):
        """Inicializa el generador de informes."""
        self.directorio_informes = "informes"
        if not os.path.exists(self.directorio_informes):
            os.makedirs(self.directorio_informes)
    
    def _obtener_nombre_archivo(self, tipo_informe):
        """
        Genera un nombre de archivo con timestamp.
        Utilizó el timestamp (fecha y hora) para crear nombres únicos.
        Esto evita que un nuevo informe sobrescriba informes anteriores,
        permitiendo un historial de reportes.
        
        Args:
            tipo_informe (str): Tipo de informe
            
        Returns:
            str: Nombre del archivo con ruta
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"{tipo_informe}_{timestamp}.csv"
        return os.path.join(self.directorio_informes, nombre)
    
    def informe_empleados(self, mostrar=True, exportar=False):
        """
        Genera informe de empleados.
        Este informe lista todos los empleados con sus datos principales.
        Si exportar=True, crea un archivo CSV que se puede abrir en Excel.
        Muestra el departamento asignado a cada empleado si existe.
        
        Args:
            mostrar (bool): Mostrar por consola
            exportar (bool): Exportar a CSV
            
        Returns:
            str: Ruta del archivo si se exportó, None en caso contrario
        """
        empleados = Empleado.listar_todos()
        
        if mostrar:
            print("\n" + "="*100)
            print("INFORME DE EMPLEADOS".center(100))
            print("="*100)
            print(f"{'RUT':<15} {'NOMBRE':<20} {'APELLIDO':<20} {'CARGO':<20} {'SALARIO':<15} {'DEPARTAMENTO':<10}")
            print("-"*100)
            
            if not empleados:
                print("No hay empleados registrados".center(100))
            else:
                for emp in empleados:
                    dept = ""
                    if emp.id_departamento:
                        depto = Departamento.leer_por_id(emp.id_departamento)
                        dept = depto.nombre if depto else "N/A"
                    
                    print(f"{emp.rut:<15} {emp.nombre:<20} {emp.apellido:<20} {emp.cargo:<20} ${emp.salario:<14,.0f} {dept:<10}")
            
            print("="*100)
        
        if exportar:
            archivo = self._obtener_nombre_archivo("informe_empleados")
            try:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['RUT', 'Nombre', 'Apellido', 'Cargo', 'Salario', 'ID Departamento', 'Departamento'])
                    
                    for emp in empleados:
                        dept = ""
                        if emp.id_departamento:
                            depto = Departamento.leer_por_id(emp.id_departamento)
                            dept = depto.nombre if depto else "N/A"
                        
                        writer.writerow([emp.rut, emp.nombre, emp.apellido, emp.cargo, emp.salario, emp.id_departamento or '', dept])
                
                print(f"\n[OK] Informe exportado a: {archivo}")
                return archivo
            except Exception as e:
                print(f"\n[ERROR] Error al exportar informe: {e}")
                return None
        
        return None
    
    def informe_departamentos(self, mostrar=True, exportar=False):
        """
        Genera informe de departamentos.
        
        Args:
            mostrar (bool): Mostrar por consola
            exportar (bool): Exportar a CSV
            
        Returns:
            str: Ruta del archivo si se exportó, None en caso contrario
        """
        departamentos = Departamento.listar_todos()
        
        if mostrar:
            print("\n" + "="*120)
            print("INFORME DE DEPARTAMENTOS".center(120))
            print("="*120)
            print(f"{'ID':<8} {'NOMBRE':<30} {'GERENTE':<30} {'DESCRIPCIÓN':<45}")
            print("-"*120)
            
            if not departamentos:
                print("No hay departamentos registrados".center(120))
            else:
                for dept in departamentos:
                    desc = dept.descripcion[:42] + "..." if len(dept.descripcion) > 45 else dept.descripcion
                    print(f"{dept.id_depto:<8} {dept.nombre:<30} {dept.gerente:<30} {desc:<45}")
            
            print("="*120)
        
        if exportar:
            archivo = self._obtener_nombre_archivo("informe_departamentos")
            try:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Nombre', 'Gerente', 'Descripción'])
                    
                    for dept in departamentos:
                        writer.writerow([dept.id_depto, dept.nombre, dept.gerente, dept.descripcion])
                
                print(f"\n[OK] Informe exportado a: {archivo}")
                return archivo
            except Exception as e:
                print(f"\n[ERROR] Error al exportar informe: {e}")
                return None
        
        return None
    
    def informe_proyectos(self, mostrar=True, exportar=False):
        """
        Genera informe de proyectos.
        
        Args:
            mostrar (bool): Mostrar por consola
            exportar (bool): Exportar a CSV
            
        Returns:
            str: Ruta del archivo si se exportó, None en caso contrario
        """
        proyectos = Proyecto.listar_todos()
        
        if mostrar:
            print("\n" + "="*130)
            print("INFORME DE PROYECTOS".center(130))
            print("="*130)
            print(f"{'ID':<8} {'NOMBRE':<25} {'FECHA INICIO':<15} {'ESTADO':<12} {'DESCRIPCIÓN':<60}")
            print("-"*130)
            
            if not proyectos:
                print("No hay proyectos registrados".center(130))
            else:
                for proy in proyectos:
                    fecha = proy.fecha_inicio.strftime("%d/%m/%Y")
                    desc = proy.descripcion[:57] + "..." if len(proy.descripcion) > 60 else proy.descripcion
                    print(f"{proy.id_proyecto:<8} {proy.nombre:<25} {fecha:<15} {proy.estado:<12} {desc:<60}")
            
            print("="*130)
        
        if exportar:
            archivo = self._obtener_nombre_archivo("informe_proyectos")
            try:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Nombre', 'Fecha Inicio', 'Estado', 'Descripción'])
                    
                    for proy in proyectos:
                        fecha = proy.fecha_inicio.strftime("%d/%m/%Y")
                        writer.writerow([proy.id_proyecto, proy.nombre, fecha, proy.estado, proy.descripcion])
                
                print(f"\n[OK] Informe exportado a: {archivo}")
                return archivo
            except Exception as e:
                print(f"\n[ERROR] Error al exportar informe: {e}")
                return None
        
        return None
    
    def informe_registros_tiempo(self, mostrar=True, exportar=False):
        """
        Genera informe de registros de tiempo.
        
        Args:
            mostrar (bool): Mostrar por consola
            exportar (bool): Exportar a CSV
            
        Returns:
            str: Ruta del archivo si se exportó, None en caso contrario
        """
        registros = RegistroTiempo.listar_todos()
        
        if mostrar:
            print("\n" + "="*130)
            print("INFORME DE REGISTROS DE TIEMPO".center(130))
            print("="*130)
            print(f"{'ID':<8} {'RUT EMPLEADO':<15} {'FECHA':<12} {'HORAS':<8} {'PROYECTO':<25} {'DESCRIPCIÓN':<50}")
            print("-"*130)
            
            total_horas = 0
            if not registros:
                print("No hay registros de tiempo".center(130))
            else:
                for reg in registros:
                    fecha = reg.fecha_registro.strftime("%d/%m/%Y")
                    desc = reg.descripcion[:47] + "..." if len(reg.descripcion) > 50 else reg.descripcion
                    print(f"{reg.id_registro:<8} {reg.empleado_rut:<15} {fecha:<12} {reg.horas:<8.1f} {reg.proyecto:<25} {desc:<50}")
                    total_horas += reg.horas
                
                print("-"*130)
                print(f"{'TOTAL DE HORAS:':<61} {total_horas:<8.1f}")
            
            print("="*130)
        
        if exportar:
            archivo = self._obtener_nombre_archivo("informe_registros_tiempo")
            try:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'RUT Empleado', 'Fecha', 'Horas', 'Proyecto', 'Descripción'])
                    
                    total_horas = 0
                    for reg in registros:
                        fecha = reg.fecha_registro.strftime("%d/%m/%Y")
                        writer.writerow([reg.id_registro, reg.empleado_rut, fecha, reg.horas, reg.proyecto, reg.descripcion])
                        total_horas += reg.horas
                    
                    writer.writerow([])
                    writer.writerow(['TOTAL DE HORAS', total_horas])
                
                print(f"\n[OK] Informe exportado a: {archivo}")
                return archivo
            except Exception as e:
                print(f"\n[ERROR] Error al exportar informe: {e}")
                return None
        
        return None
    
    def informe_asignaciones_empleado_proyecto(self, mostrar=True, exportar=False):
        """
        Genera informe de asignaciones empleado-proyecto.
        
        Args:
            mostrar (bool): Mostrar por consola
            exportar (bool): Exportar a CSV
            
        Returns:
            str: Ruta del archivo si se exportó, None en caso contrario
        """
        empleados = Empleado.listar_todos()
        
        if mostrar:
            print("\n" + "="*130)
            print("INFORME DE ASIGNACIONES EMPLEADO-PROYECTO".center(130))
            print("="*130)
            print(f"{'RUT EMPLEADO':<15} {'NOMBRE':<25} {'PROYECTOS ASIGNADOS':<80}")
            print("-"*130)
            
            hay_datos = False
            for emp in empleados:
                proyectos = Proyecto.obtener_proyectos_empleado(emp.rut)
                if proyectos:
                    hay_datos = True
                    proyecto_names = ", ".join([f"{p.nombre} ({p.estado})" for p in proyectos])
                    print(f"{emp.rut:<15} {emp.nombre + ' ' + emp.apellido:<25} {proyecto_names:<80}")
            
            if not hay_datos:
                print("No hay asignaciones empleado-proyecto".center(130))
            
            print("="*130)
        
        if exportar:
            archivo = self._obtener_nombre_archivo("informe_asignaciones_empleado_proyecto")
            try:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['RUT Empleado', 'Nombre', 'Proyectos Asignados'])
                    
                    for emp in empleados:
                        proyectos = Proyecto.obtener_proyectos_empleado(emp.rut)
                        if proyectos:
                            proyecto_names = ", ".join([f"{p.nombre} ({p.estado})" for p in proyectos])
                            writer.writerow([emp.rut, emp.nombre + ' ' + emp.apellido, proyecto_names])
                
                print(f"\n[OK] Informe exportado a: {archivo}")
                return archivo
            except Exception as e:
                print(f"\n[ERROR] Error al exportar informe: {e}")
                return None
        
        return None
    
    def generar_todos_informes_csv(self):
        """
        Genera todos los informes y los exporta a CSV.
        
        Returns:
            list: Lista de rutas de archivos generados
        """
        print("\n" + "="*80)
        print("GENERANDO TODOS LOS INFORMES...".center(80))
        print("="*80)
        
        archivos = []
        
        archivos.append(self.informe_empleados(mostrar=False, exportar=True))
        archivos.append(self.informe_departamentos(mostrar=False, exportar=True))
        archivos.append(self.informe_proyectos(mostrar=False, exportar=True))
        archivos.append(self.informe_registros_tiempo(mostrar=False, exportar=True))
        archivos.append(self.informe_asignaciones_empleado_proyecto(mostrar=False, exportar=True))
        
        archivos = [a for a in archivos if a is not None]
        
        print("\n" + "="*80)
        print(f"[OK] Se generaron {len(archivos)} informes exitosamente".center(80))
        print("="*80)
        
        return archivos
