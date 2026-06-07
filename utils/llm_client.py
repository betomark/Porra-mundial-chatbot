import os
import logging
from openai import OpenAI
# Import your Gemini client here if you are still using it
# import google.generativeai as genai 
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class LLMClient:
    """Wrapper for local or cloud LLM providers used by the application."""
    def __init__(self):
        """Initialize the configured LLM provider client."""
        logger.debug("Initializing LLMClient.")
        self.provider = os.getenv("LLM_PROVIDER", "local").lower()
        logger.info("Selected LLM provider: %s", self.provider)
        
        if self.provider == "local":
            # Point to the local Ollama server
            self.client = OpenAI(
                base_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1"),
                api_key="ollama" # Ollama does not require a key, but the library expects a string
            )
            self.model_name = os.getenv("LOCAL_LLM_MODEL", "llama3:8b")
            logger.info("Configured local LLM model: %s", self.model_name)
        else:
            logger.warning("LLM provider %s is not implemented yet.", self.provider)
            # Initialize Gemini here if you decide to use a cloud provider
            # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            pass

    def generate_prediction(self, prompt_system, prompt_user):
        """Send the cleaned SofaScore/Poisson context to the LLM."""
        logger.debug("Generating forecast with provider %s", self.provider)
        if self.provider == "local":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": prompt_system},
                        {"role": "user", "content": prompt_user}
                    ],
                    temperature=0.2 # Low temperature to avoid hallucinating statistical data
                )
                logger.info("Forecast generated successfully for provider %s", self.provider)
                return response.choices[0].message.content
            except Exception as e:
                logger.error("Error connecting to local LLM (Ollama): %s", e)
                return f"Error connecting to the local LLM (Ollama): {e}"
        else:
            logger.error("Forecast generation not implemented for provider %s", self.provider)
            # Response logic for Gemini
            # model = genai.GenerativeModel('gemini-pro')
            # ...
            return None
