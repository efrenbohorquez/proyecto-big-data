"""
Script para obtener documentos adicionales y completar la cuota de 100
Autor: Efren Bohorquez Vargas
"""

import os
import sys
from scraper_documentos_procuraduria import ScraperDocumentosProcuraduria

def main():
    print("=" * 70)
    print("OBTENCIÓN DE DOCUMENTOS ADICIONALES")
    print("=" * 70)
    print("\nObjetivo: Alcanzar mínimo 100 documentos en la base de datos")
    print("Documentos actuales: 98")
    print("Documentos a obtener: ~5 (para margen de seguridad)")
    
    try:
        # Crear scraper con objetivo bajo (solo necesitamos unos pocos)
        scraper = ScraperDocumentosProcuraduria(objetivo_documentos=5)
        
        # Ejecutar scraping
        scraper.ejecutar_scraping_masivo(descargar=True)
        
        print("\n" + "=" * 70)
        print("PROCESO COMPLETADO")
        print("=" * 70)
        print("\nPróximos pasos:")
        print("1. Ejecutar: python cargar_documentos_a_bd.py")
        print("2. Verificar conteo con: python count_docs.py")
        
    except KeyboardInterrupt:
        print("\n\n✗ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
