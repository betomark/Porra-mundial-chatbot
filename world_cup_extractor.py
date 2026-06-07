import os
import json
import time
import logging
from selenium import webdriver
import players
import teams
import events
from datafc.utils import sofascore_client
from utils.logging_config import setup_logging
from utils.mongo_client import MongoDBClient
from utils.json_store import save_json
from utils.persistence import persist

setup_logging()
logger = logging.getLogger(__name__)


def create_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-infobars")

    if os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")

    return webdriver.Chrome(options=options)


def run_extractor():
    logger.info("🚀 Iniciando navegador...")
    driver = create_chrome_driver()
    mongo = MongoDBClient()
    team_list = []

    try:
        logger.info("🌐 Cargando Sofascore...")
        driver.get("https://www.sofascore.com/es/football/tournament/world/world-championship/16#id:58210")

        # Esperamos a que cargue e interactúe la página
        time.sleep(2)
        logger.info("📜 Haciendo scroll...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        logger.info("🔍 Analizando tráfico de red y extrayendo datos...")
        logs_raw = driver.get_log("performance")

        for entry in logs_raw:
            log = json.loads(entry["message"])["message"]

            # Esta vez buscamos "Network.responseReceived" (cuando la respuesta ya llegó al navegador)
            if log["method"] == "Network.responseReceived":
                params = log["params"]
                response = params["response"]
                url = response["url"]

                # Filtramos solo las llamadas que apunten a la API de Sofascore
                if "sofascore.com/api/v1/unique-tournament/16/scheduled-events/" in url or "sofascore.com/api/v1/unique-tournament/16/season/58210/standings/total" in url or "sofascore.com/api/v1/unique-tournament/16/season/58210/power-rankings" in url:
                    request_id = params["requestId"]

                    try:
                        # Le pedimos a Chrome el cuerpo (body) de esa respuesta específica mediante su ID
                        body_data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})

                        # body_data['body'] contiene el JSON en formato texto plano (string)
                        json_texto = body_data["body"]
                        # Convertimos ese texto en un DICCIONARIO de Python real
                        datos_diccionario = json.loads(json_texto)
                        claves = datos_diccionario.keys()
                        logger.info(f"✅ Datos extraídos de {url} con claves: {claves}")
                        if "standings" in claves:
                            logger.info("📊 Guardando clasificación...")
                            persist(
                                collection="standings",
                                mongo_doc={
                                    "_id": "world_cup_2026_standings",
                                    "reference": "world_cup_2026",
                                    "data": datos_diccionario,
                                },
                                json_path="data/standings.json",
                                json_data=datos_diccionario,
                                save_json_flag=True,
                                save_mongo_flag=True,
                                filter_fields=["_id"],
                            )
                            logger.info("📋 Extrayendo datos de equipos para facilitar búsquedas futuras...")
                            team_list = teams.get_teams(datos_diccionario, store=True)
                            logger.info(f"👥 Equipos extraídos: {[team.name for team in team_list]}")
                        elif "powerRankings" in claves:
                            logger.info("📈 Guardando ranking de poder...")
                            persist(
                                collection="power_rankings",
                                mongo_doc={
                                    "_id": "world_cup_2026_power_rankings",
                                    "reference": "world_cup_2026",
                                    "data": datos_diccionario,
                                },
                                json_path="data/power_rankings.json",
                                json_data=datos_diccionario,
                                save_json_flag=True,
                                save_mongo_flag=True,
                                filter_fields=["_id"],
                            )
                        elif "events" in claves:
                            logger.info("📅 Guardando eventos programados...")
                            for evento in datos_diccionario["events"]:
                                local = evento["homeTeam"]["name"]
                                visitante = evento["awayTeam"]["name"]
                                logger.info(f"   - {local} vs {visitante} el {evento['startTimestamp']}")
                                nombre_archivo = f"data/events/scheduled_event_{local} vs {visitante} el {evento['startTimestamp']}.json"
                                evento_limpio = events.clean_pre_event(evento)
                                apuestas = events.get_odds(evento["id"])
                                evento_limpio["odds"] = apuestas
                                persist(
                                    collection="events",
                                    mongo_doc={
                                        "_id": evento["id"],
                                        "local": local,
                                        "visitante": visitante,
                                        "startTimestamp": evento["startTimestamp"],
                                        "event_data": evento_limpio,
                                    },
                                    json_path=nombre_archivo,
                                    json_data=evento_limpio,
                                    save_json_flag=True,
                                    save_mongo_flag=True,
                                    filter_fields=["_id"],
                                )

                    except Exception as e:
                        # Algunas peticiones (como respuestas 204 o pendientes) no tienen contenido y darán error aquí.
                        # Las ignoramos de forma segura.
                        logger.warning(f"⚠️ No se pudo obtener el cuerpo de la respuesta para {url}: {e}")

    except Exception as e:
        logger.error(f"❌ Ocurrió un error general: {e}")

    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning("⚠️ Error cerrando el navegador: %s", e)

    for team in team_list:
        logger.info(f"📊 Obteniendo estadísticas recientes para {team.name}...")
        team.get_team_recent_performance(store=True)
        logger.info(f"📋 Obteniendo últimos partidos para {team.name}...")
        team.get_team_last_matches(store=True)
        logger.info(f"👥 Obteniendo plantilla de {team.name}...")
        squad = team.get_team_squad(store=True)
        team_seasons = team.get_team_seasons(store=True)
        for tournament_name, tournament_data in team_seasons.items():
            tournament_id = tournament_data["tournament_id"]
            for season in tournament_data["seasons"]:
                season_id = season["season_id"]
                season_year = season["season_year"]
                logger.info(f"📈 Obteniendo estadísticas para {team.name} en {tournament_name} - {season['season_name']}...")
                team.get_team_stats(tournament_id, tournament_name, season_id, season['season_name'], season_year, store=True)
        for player in squad:
            logger.info(f"👤 Obteniendo estadísticas para el jugador {player.name}...")
            player_obj = players.Player(player.player_id, player.name)
            player_obj.get_player_total_stats(store=True)

    logger.info("✅ Extracción finalizada correctamente.")


if __name__ == "__main__":
    run_extractor()

