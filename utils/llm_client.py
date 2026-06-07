import os
from openai import OpenAI
# Importa aquí tu cliente de Gemini si lo seguías usando
# import google.generativeai as genai 

class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "local").lower()
        
        if self.provider == "local":
            # Apuntamos al servidor local de Ollama
            self.client = OpenAI(
                base_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1"),
                api_key="ollama" # Ollama no requiere Key, pero la librería exige un string
            )
            self.model_name = os.getenv("LOCAL_LLM_MODEL", "llama3:8b")
        else:
            # Aquí inicializarías Gemini si decides volver a la nube
            # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            pass

    def generar_pronostico(self, prompt_sistema, prompt_usuario):
        """Envía el contexto purificado de SofaScore/Poisson al LLM."""
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
                return response.choices[0].message.content
            except Exception as e:
                return f"Error conectando con el LLM Local (Ollama): {e}"
        else:
            # Lógica de respuesta para Gemini
            # model = genai.GenerativeModel('gemini-pro')
            # ...
            pass