# Este archivo permite que 'models' sea un paquete de Python
from .empleado import Empleado
from .departamento import Departamento
from .registro_tiempo import RegistroTiempo
from .proyecto import Proyecto

__all__ = ['Empleado', 'Departamento', 'RegistroTiempo', 'Proyecto']