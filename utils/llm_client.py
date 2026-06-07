import os
import logging
from openai import OpenAI
# Importa aquí tu cliente de Gemini si lo seguías usando
# import google.generativeai as genai 
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        logger.debug("Initializing LLMClient.")
        self.provider = os.getenv("LLM_PROVIDER", "local").lower()
        logger.info("Selected LLM provider: %s", self.provider)
        
        if self.provider == "local":
            # Apuntamos al servidor local de Ollama
            self.client = OpenAI(
                base_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1"),
                api_key="ollama" # Ollama no requiere Key, pero la librería exige un string
            )
            self.model_name = os.getenv("LOCAL_LLM_MODEL", "llama3:8b")
            logger.info("Configured local LLM model: %s", self.model_name)
        else:
            logger.warning("LLM provider %s is not implemented yet.", self.provider)
            # Aquí inicializarías Gemini si decides volver a la nube
            # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            pass

    def generar_pronostico(self, prompt_sistema, prompt_usuario):
        """Envía el contexto purificado de SofaScore/Poisson al LLM."""
        logger.debug("Generating forecast with provider %s", self.provider)
        if self.provider == "local":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    temperature=0.2 # Temperatura baja para evitar que invente datos estadísticos
                )
                logger.info("Forecast generated successfully for provider %s", self.provider)
                return response.choices[0].message.content
            except Exception as e:
                logger.error("Error connecting to local LLM (Ollama): %s", e)
                return f"Error conectando con el LLM Local (Ollama): {e}"
        else:
            logger.error("Forecast generation not implemented for provider %s", self.provider)
            # Lógica de respuesta para Gemini
            # model = genai.GenerativeModel('gemini-pro')
            # ...
            return None