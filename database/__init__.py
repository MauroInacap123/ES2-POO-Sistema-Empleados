# Este archivo permite que 'database' sea un paquete de Python
from .conexion import get_connection, create_table_empleados

__all__ = ['get_connection', 'create_table_empleados']