#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de prueba para registro de tiempo"""

from models.registro_tiempo import RegistroTiempo
from datetime import datetime

print("Probando creación de registro de tiempo...\n")

# Crear un registro
reg = RegistroTiempo(
    empleado_rut='21981220-5',
    fecha_registro=datetime(2025, 11, 13),
    horas=8.5,
    proyecto='Integrado',
    descripcion='Prueba de insert'
)

print(f"Registro creado:")
print(f"  RUT: {reg.empleado_rut}")
print(f"  Fecha: {reg.fecha_registro}")
print(f"  Horas: {reg.horas}")
print(f"  Proyecto: {reg.proyecto}")
print(f"  Descripción: {reg.descripcion}")

print("\nIntentando guardar en BD...")
resultado = reg.crear()
print(f"✓ Guardado: {resultado}")

print("\nProbando listado...")
registros = RegistroTiempo.listar_todos(limit=10)
print(f"✓ Se encontraron {len(registros)} registros")
if registros:
    print(f"\nÚltimo registro:")
    print(f"  {registros[-1]}")
