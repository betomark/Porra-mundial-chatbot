import os
import json
from google import genai
from google.genai import types
import events
import teams
import players

class gemini:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ Configura la variable de entorno GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL")
        if not self.model:
            raise ValueError("⚠️ Configura la variable de entorno GEMINI_MODEL")
        self.client = genai.Client(api_key=self.api_key)

    def _load_json(self, path):
        """Método utilitario para leer archivos JSON de forma segura."""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    
    def build_match_context(self, event_id, team_a_id, team_b_id):
        """
        Recopila selectivamente todos los JSON relacionados con un partido específico.
        Esto evita saturar la API con datos de selecciones que no van a jugar.
        """
        context = {}
        
        # 1. Datos del evento (Cuotas, probabilidades iniciales, etc.)
        context["event_odds"] = self._load_json(os.path.join(self.data_dir, "events", f"{event_id}.json"))
        
        # 2. Rankings globales (Para ver el nivel base de cada uno)
        context["power_rankings"] = self._load_json(os.path.join(self.data_dir, "power_rankings.json"))
        
        # 3. Datos específicos de los equipos involucrados
        for team_id, label in [(team_a_id, "team_A"), (team_b_id, "team_B")]:
            team_path = os.path.join(self.data_dir, "teams")
            context[f"{label}_stats"] = self._load_json(os.path.join(team_path, "stats", f"{team_id}.json"))
            context[f"{label}_performance"] = self._load_json(os.path.join(team_path, "performance", f"{team_id}.json"))
            context[f"{label}_last_matches"] = self._load_json(os.path.join(team_path, "last_matches", f"{team_id}.json"))
            # Nota: Podrías añadir squad o stats de jugadores clave aquí si lo deseas
            
        return context
    
    def generate_prediction(self, event_id, team_a_id, team_b_id):
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
                model=self.model_name,
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