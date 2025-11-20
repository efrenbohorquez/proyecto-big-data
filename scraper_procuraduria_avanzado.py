"""
Script Avanzado de Web Scraping - Procuraduría General de la Nación
Autor: Efren Bohorquez Vargas
Universidad Central
Fecha: 19 de noviembre de 2025

Este script explora recursivamente los enlaces encontrados en la página
principal de la Procuraduría y extrae información de múltiples secciones.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from helpers import WebScraper, Funciones

load_dotenv()

class ScraperProcuraduriaAvanzado:
    """
    Scraper avanzado que explora múltiples niveles de la web
    """
    
    def __init__(self, max_paginas=10):
        self.scraper = WebScraper(delay_between_requests=3.0, max_retries=3)
        self.funciones = Funciones()
        self.base_url = "https://www.procuraduria.gov.co"
        self.max_paginas = max_paginas
        self.paginas_visitadas = set()
        self.resultados = {
            "fuente": "Procuraduría General de la Nación - Scraping Avanzado",
            "url_base": self.base_url,
            "fecha_inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "configuracion": {
                "max_paginas": max_paginas,
                "delay_requests": "3.0 segundos",
                "user_agent": "Universidad Central - Proyecto Big Data"
            },
            "paginas_analizadas": [],
            "documentos_encontrados": [],
            "estadisticas": {}
        }
    
    def analizar_pagina(self, url):
        """
        Analiza una página individual y extrae toda su información
        """
        if url in self.paginas_visitadas or len(self.paginas_visitadas) >= self.max_paginas:
            return None
        
        print(f"\n{'='*70}")
        print(f"Analizando: {url}")
        print(f"Progreso: {len(self.paginas_visitadas) + 1}/{self.max_paginas}")
        print(f"{'='*70}")
        
        try:
            soup = self.scraper.obtener_pagina(url)
            
            if not soup:
                return None
            
            self.paginas_visitadas.add(url)
            
            # Extraer información
            titulo = soup.find('title')
            titulo_texto = titulo.string.strip() if titulo else "Sin título"
            
            # Textos
            textos = self.scraper.extraer_textos(soup)
            
            # Enlaces
            enlaces = self.scraper.extraer_enlaces(soup, url, filtro_dominio=True)
            
            # Buscar documentos descargables
            documentos = []
            for enlace in soup.find_all('a', href=True):
                href = enlace['href']
                if any(href.lower().endswith(ext) for ext in ['.pdf', '.docx', '.xlsx', '.doc', '.xls', '.zip']):
                    # Construir URL completa
                    if not href.startswith('http'):
                        href = self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                    
                    documentos.append({
                        "url": href,
                        "texto_enlace": enlace.get_text(strip=True),
                        "tipo": href.split('.')[-1].upper()
                    })
            
            # Tablas
            tablas = self.scraper.extraer_tablas(soup)
            
            # Guardar datos de la página
            datos_pagina = {
                "url": url,
                "titulo": titulo_texto,
                "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estadisticas": {
                    "num_textos": len(textos),
                    "num_enlaces": len(enlaces),
                    "num_documentos": len(documentos),
                    "num_tablas": len(tablas)
                },
                "muestra_contenido": textos[:3] if textos else [],
                "documentos_encontrados": documentos[:10]  # Primeros 10
            }
            
            self.resultados["paginas_analizadas"].append(datos_pagina)
            
            # Agregar documentos a la lista general
            self.resultados["documentos_encontrados"].extend(documentos)
            
            print(f"✓ Título: {titulo_texto[:60]}...")
            print(f"✓ Textos: {len(textos)}")
            print(f"✓ Enlaces: {len(enlaces)}")
            print(f"✓ Documentos: {len(documentos)}")
            print(f"✓ Tablas: {len(tablas)}")
            
            return enlaces
            
        except Exception as e:
            print(f"✗ Error al analizar {url}: {str(e)}")
            return None
    
    def explorar_recursivamente(self):
        """
        Explora el sitio de forma recursiva hasta alcanzar max_paginas
        """
        print("\n" + "="*70)
        print("EXPLORACIÓN RECURSIVA DEL SITIO WEB")
        print("="*70)
        
        # Comenzar con la página principal
        cola_urls = [self.base_url]
        
        while cola_urls and len(self.paginas_visitadas) < self.max_paginas:
            url_actual = cola_urls.pop(0)
            
            nuevos_enlaces = self.analizar_pagina(url_actual)
            
            if nuevos_enlaces:
                # Agregar nuevos enlaces a la cola (solo los que no hemos visitado)
                for enlace in nuevos_enlaces:
                    if enlace not in self.paginas_visitadas and enlace not in cola_urls:
                        if len(self.paginas_visitadas) + len(cola_urls) < self.max_paginas:
                            cola_urls.append(enlace)
        
        print(f"\n✓ Exploración completada: {len(self.paginas_visitadas)} páginas analizadas")
    
    def descargar_documentos_muestra(self, max_descargas=3):
        """
        Descarga una muestra de documentos encontrados
        """
        print("\n" + "="*70)
        print("DESCARGA DE DOCUMENTOS (MUESTRA)")
        print("="*70)
        
        self.funciones.crear_carpeta("uploads")
        documentos_descargados = []
        
        # Filtrar documentos únicos
        docs_unicos = {}
        for doc in self.resultados["documentos_encontrados"]:
            docs_unicos[doc["url"]] = doc
        
        # Descargar hasta max_descargas documentos
        for i, (url, info) in enumerate(list(docs_unicos.items())[:max_descargas]):
            print(f"\nDescargando {i+1}/{max_descargas}:")
            print(f"Tipo: {info['tipo']}")
            print(f"Descripción: {info['texto_enlace'][:50]}...")
            
            # Generar nombre de archivo seguro
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"procuraduria_doc_{i+1}_{timestamp}.{info['tipo'].lower()}"
            ruta_destino = os.path.join("uploads", nombre_archivo)
            
            try:
                if self.scraper.descargar_archivo(url, ruta_destino):
                    tamano = os.path.getsize(ruta_destino)
                    print(f"✓ Descargado: {nombre_archivo} ({tamano} bytes)")
                    
                    documentos_descargados.append({
                        "archivo": nombre_archivo,
                        "url_original": url,
                        "tipo": info['tipo'],
                        "tamano_bytes": tamano
                    })
                else:
                    print(f"✗ No se pudo descargar")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
        
        self.resultados["documentos_descargados"] = documentos_descargados
        print(f"\n✓ Total descargados: {len(documentos_descargados)}")
    
    def generar_estadisticas(self):
        """
        Genera estadísticas del scraping realizado
        """
        total_textos = sum(p["estadisticas"]["num_textos"] for p in self.resultados["paginas_analizadas"])
        total_enlaces = sum(p["estadisticas"]["num_enlaces"] for p in self.resultados["paginas_analizadas"])
        total_tablas = sum(p["estadisticas"]["num_tablas"] for p in self.resultados["paginas_analizadas"])
        
        # Contar tipos de documentos
        tipos_documentos = {}
        for doc in self.resultados["documentos_encontrados"]:
            tipo = doc["tipo"]
            tipos_documentos[tipo] = tipos_documentos.get(tipo, 0) + 1
        
        self.resultados["estadisticas"] = {
            "paginas_analizadas": len(self.paginas_visitadas),
            "total_textos_extraidos": total_textos,
            "total_enlaces_encontrados": total_enlaces,
            "total_tablas_encontradas": total_tablas,
            "total_documentos_encontrados": len(self.resultados["documentos_encontrados"]),
            "tipos_documentos": tipos_documentos,
            "documentos_descargados": len(self.resultados.get("documentos_descargados", [])),
            "fecha_finalizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generar_reporte_final(self):
        """
        Genera el reporte final en JSON
        """
        print("\n" + "="*70)
        print("GENERANDO REPORTE FINAL")
        print("="*70)
        
        self.generar_estadisticas()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"procuraduria_scraping_avanzado_{timestamp}.json"
        ruta_json = os.path.join("uploads", nombre_archivo)
        
        self.scraper.guardar_como_json(self.resultados, ruta_json)
        
        print(f"\n✓ Reporte generado: {ruta_json}")
        print(f"✓ Tamaño: {os.path.getsize(ruta_json)} bytes")
        
        # Mostrar estadísticas
        print("\n" + "-"*70)
        print("ESTADÍSTICAS DEL SCRAPING")
        print("-"*70)
        stats = self.resultados["estadisticas"]
        print(f"Páginas analizadas: {stats['paginas_analizadas']}")
        print(f"Textos extraídos: {stats['total_textos_extraidos']}")
        print(f"Enlaces encontrados: {stats['total_enlaces_encontrados']}")
        print(f"Tablas encontradas: {stats['total_tablas_encontradas']}")
        print(f"Documentos encontrados: {stats['total_documentos_encontrados']}")
        print(f"Documentos descargados: {stats['documentos_descargados']}")
        print(f"\nTipos de documentos:")
        for tipo, cantidad in stats['tipos_documentos'].items():
            print(f"  - {tipo}: {cantidad}")
        
        return ruta_json
    
    def ejecutar_scraping_completo(self, descargar_docs=True):
        """
        Ejecuta el proceso completo de scraping avanzado
        """
        print("\n" + "="*70)
        print("WEB SCRAPING AVANZADO - PROCURADURÍA GENERAL DE LA NACIÓN")
        print("Universidad Central - Proyecto Big Data")
        print("Autor: Efren Bohorquez Vargas")
        print("="*70)
        print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL Base: {self.base_url}")
        print(f"Máximo de páginas: {self.max_paginas}")
        print(f"Delay entre requests: 3.0 segundos")
        
        # Verificar robots.txt
        if not self.scraper.check_robots_txt(self.base_url):
            print("\n✗ Acceso no permitido según robots.txt")
            return False
        
        print("✓ Acceso permitido según robots.txt")
        
        # Explorar sitio
        self.explorar_recursivamente()
        
        # Descargar muestra de documentos
        if descargar_docs and self.resultados["documentos_encontrados"]:
            self.descargar_documentos_muestra(max_descargas=3)
        
        # Generar reporte
        ruta_reporte = self.generar_reporte_final()
        
        # Cerrar sesión
        self.scraper.cerrar_sesion()
        
        print("\n" + "="*70)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"✓ Reporte guardado en: {ruta_reporte}")
        print("✓ Scraping realizado éticamente respetando robots.txt")
        print("✓ Rate limiting aplicado correctamente")
        print("="*70 + "\n")
        
        return True


def main():
    """
    Función principal
    """
    print("\nConfiguración del scraping:")
    print("Por defecto se analizarán 10 páginas")
    print("Se descargarán hasta 3 documentos como muestra\n")
    
    try:
        scraper = ScraperProcuraduriaAvanzado(max_paginas=10)
        scraper.ejecutar_scraping_completo(descargar_docs=True)
        
    except KeyboardInterrupt:
        print("\n\n✗ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
