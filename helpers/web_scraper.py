# helpers/web_scraper.py
# Módulo para Web Scraping Ético con mejores prácticas
import requests
import time
import logging
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, List, Dict, Any, Union

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """
    Clase para realizar web scraping ético siguiendo las mejores prácticas:
    - Respetar robots.txt
    - Implementar rate limiting
    - Identificar el user agent
    - Manejar errores apropiadamente
    """
    
    def __init__(self, delay_between_requests: float = 1.0, max_retries: int = 3):
        """
        Inicializar el scraper con configuración ética
        
        Args:
            delay_between_requests: Tiempo de espera entre peticiones (en segundos)
            max_retries: Número máximo de reintentos para peticiones fallidas
        """
        self.delay = delay_between_requests
        self.last_request_time = 0.0
        self.session = self._create_session(max_retries)
        
        # User-Agent identificable para el scraping ético
        self.headers = {
            'User-Agent': 'Universidad Central - Proyecto Big Data (Investigación Académica)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
    
    def _create_session(self, max_retries: int) -> requests.Session:
        """Crear sesión con reintentos automáticos"""
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _respect_rate_limit(self):
        """Implementar rate limiting entre peticiones"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.delay:
            time.sleep(self.delay - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def check_robots_txt(self, base_url: str) -> str:
        """
        Verificar el archivo robots.txt del sitio
        """
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"robots.txt no encontrado en {base_url} (Status: {response.status_code})")
                return f"robots.txt no encontrado (Status: {response.status_code})"
        except Exception as e:
            logger.error(f"Error al acceder a robots.txt: {e}")
            return f"Error al acceder a robots.txt: {e}"
    
    def obtener_pagina(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """
        Obtener el contenido HTML de una página respetando rate limiting
        """
        try:
            self._respect_rate_limit()
            
            logger.info(f"Scrapeando: {url}")
            response = self.session.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP {e.response.status_code}: {e}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al acceder a {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición: {e}")
            return None
    
    def extraer_textos(self, soup: BeautifulSoup, selector: Optional[str] = None) -> List[str]:
        """
        Extraer textos de elementos HTML
        """
        if not soup:
            return []
        
        try:
            if selector:
                elementos = soup.select(selector)
            else:
                elementos = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            textos = [elem.get_text(strip=True) for elem in elementos if elem.get_text(strip=True)]
            return textos
        
        except Exception as e:
            logger.error(f"Error al extraer textos: {e}")
            return []
    
    def extraer_enlaces(self, soup: BeautifulSoup, base_url: str, filtro_dominio: bool = True) -> List[str]:
        """
        Extraer enlaces de una página
        """
        if not soup:
            return []
        
        try:
            enlaces = []
            base_domain = urlparse(base_url).netloc
            
            for link in soup.find_all('a', href=True):
                url_absoluta = urljoin(base_url, link['href'])
                
                if filtro_dominio:
                    if urlparse(url_absoluta).netloc == base_domain:
                        enlaces.append(url_absoluta)
                else:
                    enlaces.append(url_absoluta)
            
            return list(set(enlaces))  # Eliminar duplicados
        
        except Exception as e:
            logger.error(f"Error al extraer enlaces: {e}")
            return []
    
    def extraer_tablas(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """
        Extraer datos de tablas HTML
        """
        if not soup:
            return []
        
        try:
            tablas_data = []
            tablas = soup.find_all('table')
            
            for tabla in tablas:
                filas_data = []
                filas = tabla.find_all('tr')
                
                for fila in filas:
                    celdas = fila.find_all(['td', 'th'])
                    fila_data = [celda.get_text(strip=True) for celda in celdas]
                    if fila_data:
                        filas_data.append(fila_data)
                
                if filas_data:
                    tablas_data.append(filas_data)
            
            return tablas_data
        
        except Exception as e:
            logger.error(f"Error al extraer tablas: {e}")
            return []
    
    def descargar_archivo(self, url: str, ruta_destino: str) -> bool:
        """
        Descargar un archivo desde una URL
        """
        try:
            self._respect_rate_limit()
            
            logger.info(f"Descargando archivo: {url}")
            response = self.session.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(ruta_destino, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Archivo descargado: {ruta_destino}")
            return True
        
        except Exception as e:
            logger.error(f"Error al descargar archivo: {e}")
            return False
    
    def scrapear_multiples_paginas(self, urls: List[str], extractor_func=None) -> List[Dict]:
        """
        Scrapear múltiples páginas respetando rate limiting
        """
        resultados = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Procesando {i}/{len(urls)}: {url}")
            
            soup = self.obtener_pagina(url)
            
            if soup:
                if extractor_func:
                    datos = extractor_func(soup)
                else:
                    datos = {
                        'url': url,
                        'titulo': soup.title.string if soup.title else None,
                        'textos': self.extraer_textos(soup)
                    }
                
                resultados.append(datos)
            else:
                logger.warning(f"No se pudo scrapear: {url}")
        
        return resultados
    
    def guardar_como_json(self, datos: Any, ruta_archivo: str) -> bool:
        """
        Guardar datos extraídos en formato JSON
        """
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            logger.info(f"Datos guardados en: {ruta_archivo}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar JSON: {e}")
            return False
    
    def cerrar_sesion(self):
        """Cerrar la sesión de requests"""
        if self.session:
            self.session.close()
            logger.info("Sesión cerrada")


# Funciones auxiliares para casos de uso comunes

def scrapear_texto_simple(url: str, selector: Optional[str] = None) -> List[str]:
    """
    Función auxiliar para extraer texto de una página de forma simple
    """
    scraper = WebScraper()
    soup = scraper.obtener_pagina(url)
    textos = scraper.extraer_textos(soup, selector)
    scraper.cerrar_sesion()
    return textos


def scrapear_enlaces_sitio(url: str) -> List[str]:
    """
    Función auxiliar para extraer todos los enlaces de una página
    """
    scraper = WebScraper()
    soup = scraper.obtener_pagina(url)
    enlaces = scraper.extraer_enlaces(soup, url)
    scraper.cerrar_sesion()
    return enlaces
