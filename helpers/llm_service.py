import os
import google.generativeai as genai
import logging
from dotenv import load_dotenv

load_dotenv()

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no encontrada en variables de entorno")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('models/gemini-2.0-flash')
                logger.info("Servicio de LLM (Gemini) inicializado correctamente")
            except Exception as e:
                logger.error(f"Error al inicializar Gemini: {e}")
                self.model = None

    def generar_resumen(self, texto: str) -> str:
        """
        Genera un resumen del texto proporcionado usando Gemini.
        """
        if not self.model:
            return "Error: Servicio de IA no configurado (Falta API Key)."
        
        if not texto or len(texto.strip()) < 50:
            return "El texto es demasiado corto para ser resumido."

        try:
            # Limitar el texto si es muy largo para evitar errores de token limit (aunque Gemini aguanta bastante)
            texto_input = texto[:30000] 
            
            prompt = f"""
            Actúa como un analista experto de la Procuraduría. 
            Por favor, genera un resumen conciso y estructurado del siguiente documento legal o administrativo.
            Destaca los puntos clave, fechas importantes y conclusiones si las hay.
            Usa formato Markdown para el resultado.
            
            Texto del documento:
            {texto_input}
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error al generar resumen con IA: {e}")
            return f"Ocurrió un error al procesar el documento con IA: {str(e)}"

# Instancia global
llm_service = LLMService()
