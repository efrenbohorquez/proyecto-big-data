"""
Script de Web Scraping - Procuraduría General de la Nación
Autor: Efren Bohorquez Vargas
Universidad Central
Fecha: 19 de noviembre de 2025

Este script realiza web scraping ético a la página de la Procuraduría
para extraer información pública de interés académico.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from helpers import WebScraper, Funciones

# Cargar variables de entorno
load_dotenv()

class ScraperProcuraduria:
    """
    Clase para realizar web scraping específico a la Procuraduría
    """
    
    def __init__(self):
        self.scraper = WebScraper(delay_between_requests=3.0, max_retries=3)
        self.funciones = Funciones()
        self.base_url = "https://www.procuraduria.gov.co"
        self.resultados = {
            "fuente": "Procuraduría General de la Nación",
            "url_base": self.base_url,
            "fecha_scraping": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "datos_extraidos": []
        }
        
    def verificar_acceso(self):
        """
        Verifica si se puede acceder al sitio web respetando robots.txt
        """
        print("=" * 70)
        print("VERIFICACIÓN DE ACCESO ÉTICO")
        print("=" * 70)
        
        puede_acceder = self.scraper.check_robots_txt(self.base_url)
        
        if puede_acceder:
            print(f"✓ Acceso permitido a {self.base_url}")
            print("✓ robots.txt verificado correctamente")
            return True
        else:
            print(f"✗ Acceso no permitido según robots.txt")
            print("✗ No se puede continuar con el scraping")
            return False
    
    def scrapear_pagina_principal(self):
        """
        Extrae información de la página principal
        """
        print("\n" + "-" * 70)
        print("SCRAPING: Página Principal")
        print("-" * 70)
        
        try:
            soup = self.scraper.obtener_pagina(self.base_url)
            
            if soup:
                # Extraer título
                titulo = soup.find('title')
                if titulo:
                    print(f"Título: {titulo.string}")
                
                # Extraer textos principales
                textos = self.scraper.extraer_textos(soup, selector='p')
                print(f"✓ Párrafos extraídos: {len(textos)}")
                
                # Extraer enlaces
                enlaces = self.scraper.extraer_enlaces(soup, self.base_url, filtro_dominio=True)
                print(f"✓ Enlaces internos encontrados: {len(enlaces)}")
                
                # Guardar información
                self.resultados["datos_extraidos"].append({
                    "seccion": "Página Principal",
                    "url": self.base_url,
                    "titulo": titulo.string if titulo else "N/A",
                    "num_parrafos": len(textos),
                    "num_enlaces": len(enlaces),
                    "muestra_texto": textos[0] if textos else "N/A",
                    "enlaces_principales": enlaces[:10]  # Primeros 10 enlaces
                })
                
                return True
            else:
                print("✗ No se pudo obtener la página principal")
                return False
                
        except Exception as e:
            print(f"✗ Error al scrapear página principal: {str(e)}")
            return False
    
    def scrapear_seccion_noticias(self):
        """
        Extrae información de la sección de noticias
        """
        print("\n" + "-" * 70)
        print("SCRAPING: Sección de Noticias")
        print("-" * 70)
        
        url_noticias = f"{self.base_url}/portal/Noticias.page"
        
        try:
            soup = self.scraper.obtener_pagina(url_noticias)
            
            if soup:
                # Buscar títulos de noticias (pueden variar según la estructura)
                titulos_noticias = []
                
                # Intentar diferentes selectores comunes para noticias
                for selector in ['h2', 'h3', '.noticia-titulo', '.titulo-noticia', 'article h2']:
                    elementos = soup.select(selector)
                    if elementos:
                        titulos_noticias = [elem.get_text(strip=True) for elem in elementos[:10]]
                        break
                
                print(f"✓ Títulos de noticias encontrados: {len(titulos_noticias)}")
                
                # Extraer enlaces de noticias
                enlaces_noticias = self.scraper.extraer_enlaces(soup, url_noticias, filtro_dominio=True)
                print(f"✓ Enlaces de noticias: {len(enlaces_noticias)}")
                
                self.resultados["datos_extraidos"].append({
                    "seccion": "Noticias",
                    "url": url_noticias,
                    "titulos_encontrados": titulos_noticias,
                    "num_enlaces": len(enlaces_noticias),
                    "enlaces_muestra": enlaces_noticias[:5]
                })
                
                return True
            else:
                print("✗ No se pudo acceder a la sección de noticias")
                return False
                
        except Exception as e:
            print(f"✗ Error al scrapear noticias: {str(e)}")
            return False
    
    def scrapear_seccion_transparencia(self):
        """
        Extrae información de la sección de transparencia
        """
        print("\n" + "-" * 70)
        print("SCRAPING: Sección de Transparencia")
        print("-" * 70)
        
        url_transparencia = f"{self.base_url}/portal/Transparencia-y-acceso-a-informacion-publica.page"
        
        try:
            soup = self.scraper.obtener_pagina(url_transparencia)
            
            if soup:
                # Extraer textos
                textos = self.scraper.extraer_textos(soup)
                print(f"✓ Contenido extraído: {len(textos)} secciones de texto")
                
                # Buscar enlaces a documentos (PDFs, etc.)
                enlaces = soup.find_all('a', href=True)
                enlaces_documentos = [
                    enlace['href'] for enlace in enlaces 
                    if enlace['href'].endswith(('.pdf', '.docx', '.xlsx'))
                ]
                print(f"✓ Documentos encontrados: {len(enlaces_documentos)}")
                
                # Extraer tablas si existen
                tablas = self.scraper.extraer_tablas(soup)
                print(f"✓ Tablas encontradas: {len(tablas)}")
                
                self.resultados["datos_extraidos"].append({
                    "seccion": "Transparencia",
                    "url": url_transparencia,
                    "num_textos": len(textos),
                    "documentos_encontrados": len(enlaces_documentos),
                    "documentos_muestra": enlaces_documentos[:5],
                    "num_tablas": len(tablas)
                })
                
                return True
            else:
                print("✗ No se pudo acceder a la sección de transparencia")
                return False
                
        except Exception as e:
            print(f"✗ Error al scrapear transparencia: {str(e)}")
            return False
    
    def buscar_y_descargar_pdf(self, url_pdf, nombre_archivo):
        """
        Descarga un archivo PDF si se encuentra
        """
        print("\n" + "-" * 70)
        print(f"DESCARGA: {nombre_archivo}")
        print("-" * 70)
        
        try:
            # Asegurar que la carpeta uploads existe
            self.funciones.crear_carpeta("uploads")
            
            ruta_destino = os.path.join("uploads", nombre_archivo)
            
            # Descargar archivo
            resultado = self.scraper.descargar_archivo(url_pdf, ruta_destino)
            
            if resultado:
                print(f"✓ Archivo descargado: {ruta_destino}")
                print(f"✓ Tamaño: {os.path.getsize(ruta_destino)} bytes")
                
                self.resultados["datos_extraidos"].append({
                    "tipo": "Descarga de archivo",
                    "url": url_pdf,
                    "archivo": nombre_archivo,
                    "ruta": ruta_destino,
                    "tamano_bytes": os.path.getsize(ruta_destino)
                })
                
                return True
            else:
                print(f"✗ No se pudo descargar el archivo")
                return False
                
        except Exception as e:
            print(f"✗ Error al descargar archivo: {str(e)}")
            return False
    
    def generar_reporte(self):
        """
        Genera un reporte en JSON con todos los datos extraídos
        """
        print("\n" + "=" * 70)
        print("GENERANDO REPORTE")
        print("=" * 70)
        
        # Agregar resumen
        self.resultados["resumen"] = {
            "total_secciones_scrapeadas": len(self.resultados["datos_extraidos"]),
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "proyecto": "Proyecto Big Data - Universidad Central",
            "autor": "Efren Bohorquez Vargas"
        }
        
        # Guardar como JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"procuraduria_scraping_{timestamp}.json"
        ruta_json = os.path.join("uploads", nombre_archivo)
        
        self.scraper.guardar_como_json(self.resultados, ruta_json)
        
        print(f"✓ Reporte generado: {ruta_json}")
        print(f"✓ Tamaño del reporte: {os.path.getsize(ruta_json)} bytes")
        print(f"✓ Secciones procesadas: {len(self.resultados['datos_extraidos'])}")
        
        return ruta_json
    
    def ejecutar_scraping_completo(self):
        """
        Ejecuta el proceso completo de web scraping
        """
        print("\n")
        print("=" * 70)
        print("WEB SCRAPING - PROCURADURÍA GENERAL DE LA NACIÓN")
        print("Universidad Central - Proyecto Big Data")
        print("Autor: Efren Bohorquez Vargas")
        print("=" * 70)
        print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL Base: {self.base_url}")
        print(f"Delay entre requests: 3.0 segundos (scraping ético)")
        
        # Verificar acceso
        if not self.verificar_acceso():
            print("\n✗ Proceso cancelado por políticas de robots.txt")
            return False
        
        # Ejecutar scraping de diferentes secciones
        print("\n" + "=" * 70)
        print("INICIANDO EXTRACCIÓN DE DATOS")
        print("=" * 70)
        
        self.scrapear_pagina_principal()
        self.scrapear_seccion_noticias()
        self.scrapear_seccion_transparencia()
        
        # Generar reporte final
        ruta_reporte = self.generar_reporte()
        
        # Cerrar sesión
        self.scraper.cerrar_sesion()
        
        # Resumen final
        print("\n" + "=" * 70)
        print("PROCESO COMPLETADO")
        print("=" * 70)
        print(f"✓ Datos extraídos y guardados en: {ruta_reporte}")
        print(f"✓ Total de secciones procesadas: {len(self.resultados['datos_extraidos'])}")
        print("✓ Scraping realizado de forma ética respetando robots.txt")
        print("✓ Rate limiting aplicado (3 segundos entre requests)")
        print("\n" + "=" * 70)
        
        return True


def main():
    """
    Función principal
    """
    try:
        scraper_proc = ScraperProcuraduria()
        scraper_proc.ejecutar_scraping_completo()
        
    except KeyboardInterrupt:
        print("\n\n✗ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
