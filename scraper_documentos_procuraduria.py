"""
Script de Web Scraping Masivo - Documentos de la Procuraduría
Autor: Efren Bohorquez Vargas
Universidad Central
Fecha: 19 de noviembre de 2025

Este script busca y descarga documentos (PDF, DOCX, XLSX) de secciones
específicas como Normatividad, Manuales, Informes de Gestión, etc.
Objetivo: Obtener mínimo 100 documentos para análisis Big Data
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from helpers import WebScraper, Funciones
from urllib.parse import urljoin, urlparse

load_dotenv()

class ScraperDocumentosProcuraduria:
    """
    Scraper especializado en buscar y descargar documentos oficiales
    """
    
    def __init__(self, objetivo_documentos=100):
        self.scraper = WebScraper(delay_between_requests=2.0, max_retries=3)
        self.funciones = Funciones()
        self.base_url = "https://www.procuraduria.gov.co"
        self.objetivo_documentos = objetivo_documentos
        self.documentos_encontrados = []
        self.documentos_descargados = []
        self.urls_visitadas = set()
        
        # URLs específicas de secciones con documentos
        self.secciones_documentos = [
            "/portal/Normatividad.page",
            "/portal/Transparencia-y-acceso-a-informacion-publica.page",
            "/portal/Informes-de-Gestion.page",
            "/portal/Rendicion-de-cuentas.page",
            "/portal/Manuales-y-Procedimientos.page",
            "/portal/Publicaciones.page",
            "/portal/Resoluciones.page",
            "/portal/Circulares.page",
            "/portal/Conceptos.page",
            "/portal/Decretos.page",
            "/Lists/Normativa/AllItems.aspx",
            "/Lists/Manuales/AllItems.aspx",
            "/Lists/Publicaciones/AllItems.aspx",
            "/Lists/Resoluciones/AllItems.aspx",
            "/sitepages/resoluciones.aspx",
            "/sitepages/circulares.aspx",
            "/sitepages/normatividad.aspx"
        ]
        
        self.resultados = {
            "proyecto": "Big Data - Procuraduría General de la Nación",
            "objetivo": f"Mínimo {objetivo_documentos} documentos",
            "fecha_inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "secciones_exploradas": [],
            "documentos_encontrados": [],
            "documentos_descargados": [],
            "estadisticas": {}
        }
    
    def es_documento(self, url):
        """
        Verifica si una URL es un documento descargable
        """
        extensiones = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.zip', '.rar']
        return any(url.lower().endswith(ext) for ext in extensiones)
    
    def extraer_documentos_pagina(self, url):
        """
        Extrae todos los documentos de una página específica
        """
        if url in self.urls_visitadas:
            return []
        
        self.urls_visitadas.add(url)
        print(f"\n{'='*70}")
        print(f"Explorando: {url}")
        print(f"Documentos encontrados hasta ahora: {len(self.documentos_encontrados)}")
        print(f"{'='*70}")
        
        try:
            soup = self.scraper.obtener_pagina(url)
            if not soup:
                return []
            
            documentos_pagina = []
            
            # Buscar todos los enlaces
            for enlace in soup.find_all('a', href=True):
                href = enlace['href']
                
                # Construir URL completa
                if not href.startswith('http'):
                    href = urljoin(url, href)
                
                # Verificar si es un documento
                if self.es_documento(href):
                    texto_enlace = enlace.get_text(strip=True) or "Sin título"
                    extension = href.split('.')[-1].upper()
                    
                    # Evitar duplicados
                    if href not in [d['url'] for d in self.documentos_encontrados]:
                        doc_info = {
                            "url": href,
                            "titulo": texto_enlace,
                            "tipo": extension,
                            "pagina_origen": url,
                            "fecha_encontrado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        self.documentos_encontrados.append(doc_info)
                        documentos_pagina.append(doc_info)
                        
                        print(f"✓ Documento encontrado: {texto_enlace[:60]}... [{extension}]")
            
            # Buscar enlaces a otras páginas que puedan contener documentos
            if len(self.documentos_encontrados) < self.objetivo_documentos:
                enlaces_internos = []
                for enlace in soup.find_all('a', href=True):
                    href = enlace['href']
                    if not href.startswith('http'):
                        href = urljoin(url, href)
                    
                    # Solo seguir enlaces internos del dominio
                    if self.base_url in href and href not in self.urls_visitadas:
                        # Filtrar enlaces relevantes
                        keywords = ['normativ', 'manual', 'documento', 'resolucion', 
                                   'circular', 'concepto', 'decreto', 'informe', 
                                   'publicacion', 'transparencia', 'gestion']
                        
                        if any(keyword in href.lower() for keyword in keywords):
                            enlaces_internos.append(href)
                
                # Explorar enlaces internos prometedores
                for enlace_interno in enlaces_internos[:5]:  # Limitar a 5 por página
                    if len(self.documentos_encontrados) >= self.objetivo_documentos:
                        break
                    documentos_pagina.extend(self.extraer_documentos_pagina(enlace_interno))
            
            return documentos_pagina
            
        except Exception as e:
            print(f"✗ Error al explorar {url}: {str(e)}")
            return []
    
    def explorar_todas_secciones(self):
        """
        Explora todas las secciones definidas buscando documentos
        """
        print("\n" + "="*70)
        print("BÚSQUEDA MASIVA DE DOCUMENTOS")
        print(f"Objetivo: {self.objetivo_documentos} documentos")
        print("="*70)
        
        for seccion in self.secciones_documentos:
            if len(self.documentos_encontrados) >= self.objetivo_documentos:
                print(f"\n✓ Objetivo alcanzado: {len(self.documentos_encontrados)} documentos")
                break
            
            url_completa = self.base_url + seccion
            print(f"\n{'='*70}")
            print(f"Sección: {seccion}")
            print(f"{'='*70}")
            
            docs_antes = len(self.documentos_encontrados)
            self.extraer_documentos_pagina(url_completa)
            docs_nuevos = len(self.documentos_encontrados) - docs_antes
            
            self.resultados["secciones_exploradas"].append({
                "seccion": seccion,
                "url": url_completa,
                "documentos_encontrados": docs_nuevos
            })
            
            print(f"\n✓ Documentos encontrados en esta sección: {docs_nuevos}")
            print(f"✓ Total acumulado: {len(self.documentos_encontrados)}")
        
        # Si no alcanzamos el objetivo, hacer búsqueda más profunda
        if len(self.documentos_encontrados) < self.objetivo_documentos:
            print("\n⚠ Objetivo no alcanzado, realizando búsqueda profunda...")
            self.busqueda_profunda()
    
    def busqueda_profunda(self):
        """
        Búsqueda más profunda explorando la página principal y siguiendo enlaces
        """
        print("\n" + "="*70)
        print("BÚSQUEDA PROFUNDA ACTIVADA")
        print("="*70)
        
        # Explorar página principal
        soup = self.scraper.obtener_pagina(self.base_url)
        if soup:
            enlaces = soup.find_all('a', href=True)
            urls_por_explorar = []
            
            for enlace in enlaces:
                href = enlace['href']
                if not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                if self.base_url in href and href not in self.urls_visitadas:
                    urls_por_explorar.append(href)
            
            # Explorar URLs hasta alcanzar objetivo
            for url in urls_por_explorar:
                if len(self.documentos_encontrados) >= self.objetivo_documentos:
                    break
                self.extraer_documentos_pagina(url)
    
    def descargar_documentos(self, max_descargas=None):
        """
        Descarga los documentos encontrados
        """
        if not max_descargas:
            max_descargas = min(len(self.documentos_encontrados), self.objetivo_documentos)
        
        print("\n" + "="*70)
        print(f"DESCARGANDO DOCUMENTOS ({max_descargas} de {len(self.documentos_encontrados)})")
        print("="*70)
        
        self.funciones.crear_carpeta("uploads/documentos_procuraduria")
        
        for i, doc in enumerate(self.documentos_encontrados[:max_descargas], 1):
            print(f"\n[{i}/{max_descargas}] Descargando:")
            print(f"Título: {doc['titulo'][:60]}...")
            print(f"Tipo: {doc['tipo']}")
            
            # Generar nombre de archivo único y seguro
            nombre_base = doc['titulo'][:50].replace('/', '_').replace('\\', '_')
            nombre_base = ''.join(c for c in nombre_base if c.isalnum() or c in (' ', '-', '_')).strip()
            
            if not nombre_base:
                nombre_base = f"documento_{i}"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{i:03d}_{nombre_base}_{timestamp}.{doc['tipo'].lower()}"
            ruta_destino = os.path.join("uploads", "documentos_procuraduria", nombre_archivo)
            
            try:
                if self.scraper.descargar_archivo(doc['url'], ruta_destino):
                    if os.path.exists(ruta_destino):
                        tamano = os.path.getsize(ruta_destino)
                        print(f"✓ Descargado: {tamano:,} bytes")
                        
                        self.documentos_descargados.append({
                            "numero": i,
                            "archivo": nombre_archivo,
                            "url_original": doc['url'],
                            "titulo": doc['titulo'],
                            "tipo": doc['tipo'],
                            "tamano_bytes": tamano,
                            "ruta": ruta_destino
                        })
                    else:
                        print(f"✗ Error: archivo no se creó")
                else:
                    print(f"✗ Error al descargar")
                    
            except Exception as e:
                print(f"✗ Error: {str(e)}")
            
            # Mostrar progreso
            if i % 10 == 0:
                print(f"\n{'='*70}")
                print(f"Progreso: {i}/{max_descargas} documentos descargados")
                print(f"{'='*70}")
        
        print(f"\n✓ Descarga completada: {len(self.documentos_descargados)} documentos")
    
    def generar_reporte_final(self):
        """
        Genera el reporte final con estadísticas
        """
        print("\n" + "="*70)
        print("GENERANDO REPORTE FINAL")
        print("="*70)
        
        # Estadísticas por tipo de documento
        tipos_docs = {}
        for doc in self.documentos_encontrados:
            tipo = doc['tipo']
            tipos_docs[tipo] = tipos_docs.get(tipo, 0) + 1
        
        self.resultados["documentos_encontrados"] = self.documentos_encontrados
        self.resultados["documentos_descargados"] = self.documentos_descargados
        self.resultados["estadisticas"] = {
            "total_documentos_encontrados": len(self.documentos_encontrados),
            "total_documentos_descargados": len(self.documentos_descargados),
            "secciones_exploradas": len(self.resultados["secciones_exploradas"]),
            "tipos_documentos": tipos_docs,
            "objetivo_alcanzado": len(self.documentos_encontrados) >= self.objetivo_documentos,
            "fecha_finalizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Guardar JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_json = f"procuraduria_documentos_masivos_{timestamp}.json"
        ruta_json = os.path.join("uploads", nombre_json)
        
        self.scraper.guardar_como_json(self.resultados, ruta_json)
        
        # Mostrar resumen
        print(f"\n{'='*70}")
        print("ESTADÍSTICAS FINALES")
        print(f"{'='*70}")
        print(f"Objetivo: {self.objetivo_documentos} documentos")
        print(f"Documentos encontrados: {len(self.documentos_encontrados)}")
        print(f"Documentos descargados: {len(self.documentos_descargados)}")
        print(f"Secciones exploradas: {len(self.resultados['secciones_exploradas'])}")
        print(f"Páginas visitadas: {len(self.urls_visitadas)}")
        print(f"\nTipos de documentos encontrados:")
        for tipo, cantidad in sorted(tipos_docs.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tipo}: {cantidad}")
        
        if len(self.documentos_encontrados) >= self.objetivo_documentos:
            print(f"\n✓ ¡OBJETIVO ALCANZADO!")
        else:
            print(f"\n⚠ Objetivo parcial: {len(self.documentos_encontrados)}/{self.objetivo_documentos}")
        
        print(f"\nReporte guardado en: {ruta_json}")
        print(f"Documentos en: uploads/documentos_procuraduria/")
        print("="*70)
        
        return ruta_json
    
    def ejecutar_scraping_masivo(self, descargar=True):
        """
        Ejecuta el proceso completo de scraping masivo
        """
        print("\n" + "="*70)
        print("SCRAPING MASIVO DE DOCUMENTOS - PROCURADURÍA")
        print("Universidad Central - Proyecto Big Data")
        print("Autor: Efren Bohorquez Vargas")
        print("="*70)
        print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Objetivo: Mínimo {self.objetivo_documentos} documentos")
        print(f"Delay entre requests: 2.0 segundos")
        
        # Verificar robots.txt
        if not self.scraper.check_robots_txt(self.base_url):
            print("\n✗ Acceso no permitido según robots.txt")
            return False
        
        print("✓ Acceso permitido según robots.txt\n")
        
        inicio = time.time()
        
        # Explorar secciones
        self.explorar_todas_secciones()
        
        # Descargar documentos
        if descargar and self.documentos_encontrados:
            self.descargar_documentos()
        
        # Generar reporte
        self.generar_reporte_final()
        
        # Cerrar sesión
        self.scraper.cerrar_sesion()
        
        tiempo_total = time.time() - inicio
        
        print("\n" + "="*70)
        print("PROCESO COMPLETADO")
        print("="*70)
        print(f"Tiempo total: {tiempo_total/60:.2f} minutos")
        print(f"Documentos encontrados: {len(self.documentos_encontrados)}")
        print(f"Documentos descargados: {len(self.documentos_descargados)}")
        print("="*70 + "\n")
        
        return True


def main():
    """
    Función principal
    """
    print("\n" + "="*70)
    print("CONFIGURACIÓN DEL SCRAPING MASIVO")
    print("="*70)
    print("Objetivo: Mínimo 100 documentos")
    print("Fuente: Procuraduría General de la Nación")
    print("Secciones: Normatividad, Manuales, Informes, etc.")
    print("="*70 + "\n")
    
    try:
        scraper = ScraperDocumentosProcuraduria(objetivo_documentos=100)
        scraper.ejecutar_scraping_masivo(descargar=True)
        
    except KeyboardInterrupt:
        print("\n\n✗ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
