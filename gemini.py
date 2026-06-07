import os
import json
import logging
from google import genai
from google.genai import types
import events
import teams
import players
from utils.logging_config import setup_logging
from utils.mongo_client import MongoDBClient

setup_logging()
logger = logging.getLogger(__name__)

class gemini:
    def __init__(self, api_key=None, model=None):
        logger.debug("Initializing Gemini class.")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("⚠️ GEMINI_API_KEY environment variable not configured.")
            raise ValueError("⚠️ Configura la variable de entorno GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL")
        if not self.model:
            logger.error("⚠️ GEMINI_MODEL environment variable not configured.")
            raise ValueError("⚠️ Configura la variable de entorno GEMINI_MODEL")
        self.client = genai.Client(api_key=self.api_key)
        self.mongo = MongoDBClient()
        self.data_dir = os.getenv("DATA_DIR", "data")
        logger.debug("Gemini class initialized successfully.")

    def _load_json(self, path):
        logger.debug(f"Attempting to load JSON from: {path}")
        """Método utilitario para leer archivos JSON de forma segura."""
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Successfully loaded JSON from: {path}")
                    return data
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {path}: {e}")
                return None
            except Exception as e:
                logger.error(f"An unexpected error occurred while loading JSON from {path}: {e}")
                return None
        logger.warning(f"File not found: {path}")
        return None

    def _load_json_or_mongo(self, path, collection_name, query, data_key="data"):
        logger.debug("Attempting to load from MongoDB collection %s with query %s", collection_name, query)
        mongo_doc = self.mongo.find_one(collection_name, query)
        if mongo_doc:
            logger.info("Loaded document from MongoDB collection %s", collection_name)
            return mongo_doc.get(data_key, mongo_doc)
        return self._load_json(path)
    
    
    def build_match_context(self, event_id, team_a_id, team_b_id):
        logger.debug(f"Building match context for event_id={event_id}, team_a_id={team_a_id}, team_b_id={team_b_id}")
        """
        Recopila selectivamente todos los JSON relacionados con un partido específico.
        Esto evita saturar la API con datos de selecciones que no van a jugar.
        """
        context = {}
        
        # 1. Datos del evento (Cuotas, probabilidades iniciales, etc.)
        context["event_odds"] = self._load_json_or_mongo(
            os.path.join(self.data_dir, "events", f"{event_id}.json"),
            "events",
            {"_id": event_id},
            data_key="event_data"
        )
        
        # 2. Rankings globales (Para ver el nivel base de cada uno)
        context["power_rankings"] = self._load_json_or_mongo(
            os.path.join(self.data_dir, "power_rankings.json"),
            "power_rankings",
            {"_id": "world_cup_2026_power_rankings"},
            data_key="data"
        )
        
        # 3. Datos específicos de los equipos involucrados
        for team_id, label in [(team_a_id, "team_A"), (team_b_id, "team_B")]:
            team_path = os.path.join(self.data_dir, "teams")
            context[f"{label}_stats"] = self._load_json(os.path.join(team_path, "stats", f"{team_id}.json"))
            context[f"{label}_performance"] = self._load_json(os.path.join(team_path, "performance", f"{team_id}.json"))
            context[f"{label}_last_matches"] = self._load_json(os.path.join(team_path, "last_matches", f"{team_id}.json"))
            team_doc = self.mongo.find_one("teams", {"_id": int(team_id) if str(team_id).isdigit() else team_id})
            if team_doc:
                context[f"{label}_summary"] = team_doc
            # Nota: Podrías añadir squad o stats de jugadores clave aquí si lo deseas
            
        logger.info(f"Match context built for event_id={event_id}")
        return context
    
    def generate_prediction(self, event_id, team_a_id, team_b_id):
        logger.debug(f"Generating prediction for event_id={event_id}, team_a_id={team_a_id}, team_b_id={team_b_id}")
        """Genera el pronóstico final enviando el contexto filtrado a Gemini."""
        # Obtenemos solo los datos que importan para este partido
        match_data = self.build_match_context(event_id, team_a_id, team_b_id)
        
        # Creamos el prompt del sistema (instrucciones de comportamiento)
        system_instruction = """
        Eres un sistema de Inteligencia Artificial experto en analítica deportiva aplicada al fútbol. Tu foco es el análisis de partidos de la copa del mundo 2026.
        Tu objetivo es analizar los datos JSON proporcionados (datos del encuentro ,estadísticas de equipos, rendimientos recientes, rankings de poder, cuotas de apuestas en vivo/pre-partido de SofaScore y los datos estadísticos de los integrantes de cada equipo) para realizar un pronóstico deportivo altamente fundamentado.
        Además debes buscar en internet información adicional relevante sobre el partido, como noticias de última hora, cuotas en casas de apuestas, lesiones, sanciones o cualquier otro factor que pueda influir en el resultado, y que no esté reflejado en los datos JSON proporcionados. Para esto, puedes realizar búsquedas en Google utilizando la función google_search(query) que tienes disponible.
        Integra la información en tiempo real de Google con los datos JSON para tu pronóstico final.

        Debes estructurar tu análisis en:
        1. ANÁLISIS DE ESTADO (Comparativa de stats y rendimiento reciente de ambos equipos).
        2. ANÁLISIS DEL MERCADO (Qué opinan las casas de apuestas según el JSON del evento y si hay valor en las cuotas).
        3. PRONÓSTICO FINAL (Resultado más probable 1X2, porcentaje de confianza y justificación breve).
        4. DISTRIBUCIÓN DE PROBABILIDADES (Si es posible, asigna probabilidades a diferentes resultados basándote en los datos).
        5. FACTORES EXTERNOS (Cualquier información adicional encontrada en Google que pueda afectar el resultado).
        """
        
        # Formateamos el JSON consolidado del partido como texto para Gemini
        data_payload = json.dumps(match_data, indent=2, ensure_ascii=False)
        
        prompt = f"Analiza el siguiente partido y genera un pronóstico detallado:\n\n```json\n{data_payload}\n```"
        
        try:
            # Enviamos tanto las instrucciones de comportamiento como los datos del partido
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="Eres un analista de datos deportivos experto...",
                    # Así se activa el Grounding con Google Search en el nuevo SDK
                    tools=[types.Tool(google_search=types.GoogleSearch())] 
                )
            )
            return response.text
        except Exception as e:
            return f"Error al generar el pronóstico: {str(e)}"