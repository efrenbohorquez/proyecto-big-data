# helpers/funciones.py
# Funciones generales de utilidad para el proyecto Big Data
import os
import zipfile
import requests
import logging
from pathlib import Path
from typing import Optional, List, Union

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Funciones:
    """Clase con funciones auxiliares para gestión de archivos y web scraping"""
    
    def __init__(self):
        self.upload_folder = 'uploads'
        self.extensiones_permitidas = ['.txt', '.json', '.csv', '.pdf', '.zip', '.docx']
    
    def crear_carpeta(self, nombre: str) -> str:
        """Crea una carpeta si no existe"""
        if not os.path.exists(nombre):
            os.makedirs(nombre)
            logger.info(f"Carpeta '{nombre}' creada exitosamente.")
        return nombre
    
    def verificar_extensiones_permitidas(self, nombre_archivo: str, extensiones_validas: Optional[List[str]] = None) -> bool:
        """Valida que el archivo tenga una extensión permitida."""
        if extensiones_validas is None:
            extensiones_validas = self.extensiones_permitidas
        
        extension = Path(nombre_archivo).suffix.lower()
        return extension in extensiones_validas
    
    def descargar_archivo(self, url: str, carpeta_destino: str = 'uploads') -> Optional[str]:
        """Descarga un archivo desde una URL usando Requests."""
        try:
            self.crear_carpeta(carpeta_destino)
            
            # Obtener nombre del archivo desde la URL
            nombre_archivo = url.split('/')[-1] or 'archivo_descargado'
            ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
            
            logger.info(f"Descargando desde: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(ruta_destino, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Archivo descargado: {ruta_destino}")
            return ruta_destino
        
        except Exception as e:
            logger.error(f"Error al descargar archivo: {e}")
            return None
    
    def descomprimir_archivo(self, archivo_zip: str, destino: str = 'uploads') -> Optional[List[str]]:
        """Descomprime un archivo ZIP."""
        try:
            self.crear_carpeta(destino)
            
            archivos_extraidos = []
            with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                zip_ref.extractall(destino)
                archivos_extraidos = zip_ref.namelist()
            
            logger.info(f"Archivos extraídos: {len(archivos_extraidos)}")
            return [os.path.join(destino, f) for f in archivos_extraidos]
        
        except Exception as e:
            logger.error(f"Error al descomprimir archivo: {e}")
            return None
    
    def descargar_y_descomprimir(self, url_archivo: str, carpeta_destino: str = 'uploads') -> Optional[List[str]]:
        """Descarga un archivo desde una URL y lo descomprime si es ZIP."""
        try:
            # Descargar el archivo
            ruta_descargada = self.descargar_archivo(url_archivo, carpeta_destino)
            
            if not ruta_descargada:
                return None
            
            # Si es un ZIP, descomprimir
            if ruta_descargada.endswith('.zip'):
                archivos_extraidos = self.descomprimir_archivo(ruta_descargada, carpeta_destino)
                
                # Eliminar el ZIP después de extraer (opcional)
                os.remove(ruta_descargada)
                logger.info(f"Archivo ZIP eliminado: {ruta_descargada}")
                
                return archivos_extraidos
            else:
                return [ruta_descargada]
        
        except Exception as e:
            logger.error(f"Error en descargar_y_descomprimir: {e}")
            return None
    
    # ========== FUNCIONES PARA PLN Y OCR ==========
    
    def extraer_texto_pdf(self, ruta_pdf: str) -> Optional[str]:
        """Extrae texto de un archivo PDF."""
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(ruta_pdf)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() + "\n"
            
            return texto.strip()
        except ImportError:
            logger.error("Librería pypdf no instalada.")
            return None
        except Exception as e:
            logger.error(f"Error al extraer texto de PDF {ruta_pdf}: {e}")
            return None

    def extraer_texto_docx(self, ruta_docx: str) -> Optional[str]:
        """Extrae texto de un archivo DOCX."""
        try:
            import docx
            
            doc = docx.Document(ruta_docx)
            texto = "\n".join([para.text for para in doc.paragraphs])
            return texto.strip()
        except ImportError:
            logger.error("Librería python-docx no instalada.")
            return None
        except Exception as e:
            logger.error(f"Error al extraer texto de DOCX {ruta_docx}: {e}")
            return None
            
    def extraer_texto_archivo(self, ruta_archivo: str) -> Optional[str]:
        """Función wrapper para extraer texto según la extensión."""
        if not os.path.exists(ruta_archivo):
            return None
            
        ext = Path(ruta_archivo).suffix.lower()
        
        if ext == '.pdf':
            return self.extraer_texto_pdf(ruta_archivo)
        elif ext in ['.docx', '.doc']: # .doc no soportado nativamente por python-docx, pero lo intentamos si es .docx renombrado
            if ext == '.docx':
                return self.extraer_texto_docx(ruta_archivo)
            else:
                logger.warning(f"Formato .doc no soportado para extracción de texto: {ruta_archivo}")
                return None
        else:
            logger.warning(f"Formato no soportado para extracción: {ext}")
            return None
