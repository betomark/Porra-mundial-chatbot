import urls
import utils.sofascore_client
import json
import logging
from scipy.stats import poisson
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def clean_pre_event(evento):
    logger.debug("Cleaning pre-event data for event id %s", evento.get("id"))
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

    logger.info("Pre-event cleaned for event id %s", evento.get("id"))
    return evento_limpio

def clean_past_event(evento):
    logger.debug("Cleaning past-event data for event id %s", evento.get("id"))
    evento_limpio = clean_pre_event(evento)
    evento_limpio["homeScore"] = evento["homeScore"]
    evento_limpio["awayScore"] = evento["awayScore"]
    # TODO: añadir más campos relevantes de eventos pasados, como goleadores, tarjetas, etc.
    logger.info("Past event cleaned for event id %s", evento.get("id"))
    return evento_limpio

def get_odds(event_id):
    url = urls.MATCH_ODDS.format(event_id=event_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    logger.info("Obteniendo cuotas para el evento %s desde %s", event_id, url)
    result = sofascore_client.get(url)
    logger.info("Cuotas obtenidas para el evento %s", event_id)
    return result

class Event:
    def __init__(self, event_id, equipo_local, equipo_visitante):
        logger.debug("Initializing Event class for event_id=%s, local=%s, visitante=%s", event_id, equipo_local, equipo_visitante)
        self.event_id = event_id
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
        self.max_goles = 7  # Límite superior razonable para calcular probabilidades

    def _fraction_to_decimal(self, frac_str):
        logger.debug("Converting fractional odds '%s' to decimal.", frac_str)
        """Convierte cuotas fraccionarias de SofaScore ('11/5') a formato decimal."""
        try:
            num, den = map(int, frac_str.split('/'))
            return round((num / den) + 1, 2)
        except (ValueError, AttributeError) as e:
            logger.warning("Could not convert fractional odds '%s': %s", frac_str, e)
            return None

    def _procesar_cuotas_evento(self, json_evento):
        logger.debug("Processing event odds.")
        """Extrae las cuotas del mercado 1X2 del JSON del evento."""
        cuotas_procesadas = {}
        if not json_evento:
            logger.warning("No JSON event data provided for odds processing.")
            return cuotas_procesadas

        markets = json_evento.get("odds", {}).get("markets", [])
        for market in markets:
            if market.get("marketGroup") == "1X2":
                for choice in market.get("choices", []):
                    name = choice.get("name")  # "1", "X" o "2"
                    frac_val = choice.get("fractionalValue")
                    cuotas_procesadas[name] = self._fraction_to_decimal(frac_val)
        logger.info("Processed %d odds entries for event.", len(cuotas_procesadas))
        return cuotas_procesadas

    def calcular_probabilidades_poisson(self, xg_local, xg_visitante):
        logger.debug("Calculating Poisson probabilities for xG_local=%s, xG_visitante=%s", xg_local, xg_visitante)
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
                prob_marcador = (poisson.pmf(goles_local, xg_local) * poisson.pmf(goles_visitante, xg_visitante))

                if goles_local > goles_visitante:
                    prob_local += prob_marcador
                elif goles_local == goles_visitante:
                    prob_empate += prob_marcador
                else:
                    prob_visitante += prob_marcador

        total = prob_local + prob_empate + prob_visitante
        if total == 0:
            logger.warning("Total probability is zero in Poisson calculation for xG_local=%s, xG_visitante=%s", xg_local, xg_visitante)
            return {
                "modelo_matematico_1X2": {
                    "1_Victoria_Local": 0.0,
                    "X_Empate": 0.0,
                    "2_Victoria_Visitante": 0.0
                },
                "estadisticas_base": {
                    "xG_Local": xg_local,
                    "xG_Visitante": xg_visitante
                }
            }

        probabilities = {
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
        logger.info("Poisson probabilities calculated for event %s", self.event_id)
        return probabilities

    def empaquetar_contexto_para_llm(self, json_sofascore, xg_local, xg_visitante):
        logger.debug("Packaging context for LLM for event %s", self.event_id)
        """
        Une el cálculo matemático puro con los datos de SofaScore
        para entregárselo pre-procesado a Gemini.
        """
        calculo_quant = self.calcular_probabilidades_poisson(xg_local, xg_visitante)

        payload_final = {
            "informacion_partido": f"{self.equipo_local} vs {self.equipo_visitante}",
            "datos_sofascore": json_sofascore,
            "analisis_poisson": calculo_quant
        }

        logger.info("LLM payload packaged for event %s", self.event_id)
        return json.dumps(payload_final, indent=2, ensure_ascii=False)
