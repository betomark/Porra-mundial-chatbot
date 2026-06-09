import urls
from datafc.utils._client import SofascoreClient
import json
from scipy.stats import poisson

def clean_pre_event(evento):
    evento_limpio = {
        "id": evento["id"],
        "customId": evento["customId"],
        "slug": evento["slug"],
        "startTimestamp": evento["startTimestamp"],
        "homeTeam": {
            "id": evento["homeTeam"]["id"],
            "name": evento["homeTeam"]["name"],
            "ranking": evento["homeTeam"]["ranking"],
            "namecode": evento["homeTeam"]["nameCode"]
        },
        "awayTeam": {
            "id": evento["awayTeam"]["id"],
            "name": evento["awayTeam"]["name"],
            "ranking": evento["awayTeam"]["ranking"],
            "namecode": evento["awayTeam"]["nameCode"]
        },
        "tournament": {
            "id": evento["uniqueTournament"]["id"],
            "name": evento["uniqueTournament"]["name"]
        },
        "season": {
            "id": evento["season"]["id"],
            "name": evento["season"]["name"]
        }
    }

    return evento_limpio

def clean_past_event(evento):
    evento_limpio = clean_pre_event(evento)
    evento_limpio["homeScore"] = evento["homeScore"]
    evento_limpio["awayScore"] = evento["awayScore"]
    #TODO: añadir más campos relevantes de eventos pasados, como goleadores, tarjetas, etc.
    return evento_limpio

class Event:
    def __init__(self, event_id, equipo_local, equipo_visitante):
        self.event_id = event_id
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
        self.client = SofascoreClient()
        self.max_goles = 7 # Límite superior razonable para calcular probabilidades

    def _fraction_to_decimal(self, frac_str):
        """Convierte cuotas fraccionarias de SofaScore ('11/5') a formato decimal."""
        try:
            num, den = map(int, frac_str.split('/'))
            return round((num / den) + 1, 2)
        except (ValueError, AttributeError):
            return None

    def _procesar_cuotas_evento(self, json_evento):
        """Extrae las cuotas del mercado 1X2 del JSON del evento."""
        cuotas_procesadas = {}
        if not json_evento:
            return cuotas_procesadas

        markets = json_evento.get("odds", {}).get("markets", [])
        for market in markets:
            if market.get("marketGroup") == "1X2":
                for choice in market.get("choices", []):
                    name = choice.get("name") # "1", "X" o "2"
                    frac_val = choice.get("fractionalValue")
                    cuotas_procesadas[name] = self._fraction_to_decimal(frac_val)
        return cuotas_procesadas
    
    def get_event_stats(self, store=False, clean=False):
        url = urls.MATCH_STATS.format(event_id=self.event_id)
        print(f"Obteniendo estadísticas para el evento {self.event_id} desde {url}...")
        try:
            event_stats = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas para el evento {self.event_id}")
            event_stats = None
        return event_stats
    
    def get_event_lineups(self):
        url = urls.MATCH_LINEUPS.format(event_id=self.event_id)
        print(f"Obteniendo alineaciones para el evento {self.event_id} desde {url}...")
        try:
            lineups = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las alineaciones para el evento {self.event_id}")
            lineups = None
        return lineups
    
    def get_event_votes(self):
        url = urls.MATCH_VOTES.format(event_id=self.event_id)
        print(f"Obteniendo votaciones para el evento {self.event_id} desde {url}...")
        try:
            votes = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las votaciones para el evento {self.event_id}")
            votes = None
        return votes
    
    def get_odds(self):
        url = urls.MATCH_ODDS.format(event_id=self.event_id)
        print(f"Obteniendo cuotas para el evento {self.event_id} desde {url}...")
        try:
            odds_data = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las cuotas para el evento {self.event_id}")
            odds_data = None
        return odds_data

    def calcular_probabilidades_poisson(self, xg_local, xg_visitante):
        """
        Calcula las probabilidades de 1, X, 2 usando la distribución de Poisson 
        basándose en los Goles Esperados (xG) de ambos equipos.
        """
        prob_local = 0.0
        prob_empate = 0.0
        prob_visitante = 0.0
        
        # Generamos una matriz de probabilidades para cada marcador exacto (ej. 1-0, 1-1, 2-1)
        # Iteramos desde 0 hasta el límite de goles establecido
        for goles_local in range(self.max_goles + 1):
            for goles_visitante in range(self.max_goles + 1):
                
                # Calculamos la probabilidad de marcar esta cantidad exacta de goles
                # P(goles_A) * P(goles_B)
                prob_marcador = (poisson.pmf(goles_local, xg_local) * poisson.pmf(goles_visitante, xg_visitante))
                
                # Clasificamos esa probabilidad en 1, X o 2
                if goles_local > goles_visitante:
                    prob_local += prob_marcador
                elif goles_local == goles_visitante:
                    prob_empate += prob_marcador
                else:
                    prob_visitante += prob_marcador

        # Normalizamos ligeramente por si el límite truncó un % residual mínimo (partidos de +8 goles)
        total = prob_local + prob_empate + prob_visitante
        
        # Formateamos el resultado como un diccionario con porcentajes
        return {
            "modelo_matematico_1X2": {
                "1_Victoria_Local": round((prob_local / total) * 100, 2),
                "X_Empate": round((prob_empate / total) * 100, 2),
                "2_Victoria_Visitante": round((prob_visitante / total) * 100, 2)
            },
            "estadisticas_base": {
                "xG_Local": xg_local,
                "xG_Visitante": xg_visitante
            }
        }

    def empaquetar_contexto_para_llm(self, json_sofascore, xg_local, xg_visitante):
        """
        Une el cálculo matemático puro con los datos de SofaScore
        para entregárselo pre-procesado a Gemini.
        """
        # 1. Ejecutamos nuestro modelo predictivo matemático
        calculo_quant = self.calcular_probabilidades_poisson(xg_local, xg_visitante)
        
        # 2. Creamos el payload final
        payload_final = {
            "informacion_partido": f"{self.equipo_local} vs {self.equipo_visitante}",
            "datos_sofascore": json_sofascore,
            "analisis_poisson": calculo_quant
        }
        
        return json.dumps(payload_final, indent=2, ensure_ascii=False)