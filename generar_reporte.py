"""
Script de Utilidad - Resumen del Proyecto
Genera un reporte con el estado actual del proyecto
"""

import os
from pathlib import Path


def contar_lineas_codigo(archivo):
    """Cuenta líneas de código en un archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

def generar_reporte():
    """Genera reporte del proyecto"""
    
    print("=" * 80)
    print("REPORTE DEL PROYECTO BIG DATA")
    print("Universidad Central - Maestría en Analítica")
    print("=" * 80)
    print()
    
    # Archivos principales
    archivos_python = list(Path('.').glob('*.py'))
    archivos_helpers = list(Path('helpers').glob('*.py'))
    archivos_templates = list(Path('templates').glob('*.html'))
    
    # Contar líneas
    total_lineas = 0
    
    print("📁 ARCHIVOS PRINCIPALES:")
    print("-" * 80)
    for archivo in archivos_python:
        if archivo.name != '__init__.py':
            lineas = contar_lineas_codigo(archivo)
            total_lineas += lineas
            print(f"   {archivo.name:<40} {lineas:>5} líneas")
    
    print()
    print("📁 MÓDULOS HELPERS:")
    print("-" * 80)
    for archivo in archivos_helpers:
        if archivo.name != '__init__.py':
            lineas = contar_lineas_codigo(archivo)
            total_lineas += lineas
            print(f"   {archivo.name:<40} {lineas:>5} líneas")
    
    print()
    print("📁 TEMPLATES HTML:")
    print("-" * 80)
    for archivo in archivos_templates:
        lineas = contar_lineas_codigo(archivo)
        print(f"   {archivo.name:<40} {lineas:>5} líneas")
    
    print()
    print("=" * 80)
    print(f"TOTAL DE LÍNEAS DE CÓDIGO PYTHON: {total_lineas}")
    print("=" * 80)
    print()
    
    # Estructura de directorios
    print("📂 ESTRUCTURA DEL PROYECTO:")
    print("-" * 80)
    estructura = {
        'Archivos Python': len(archivos_python),
        'Módulos Helpers': len(archivos_helpers),
        'Templates HTML': len(archivos_templates),
        'Archivos de configuración': len(list(Path('.').glob('*.txt'))) + len(list(Path('.').glob('*.md'))),
    }
    
    for nombre, cantidad in estructura.items():
        print(f"   {nombre:<40} {cantidad:>5} archivos")
    
    print()
    print("=" * 80)
    print("✅ Reporte generado exitosamente")
    print("=" * 80)

if __name__ == "__main__":
    generar_reporte()
