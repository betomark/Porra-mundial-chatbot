import json
import time
from selenium import webdriver
import players
import teams
import events


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

print("🚀 Iniciando navegador...")
driver = webdriver.Chrome(options=options)

# Aquí guardaremos todas las respuestas de la API
# La clave será la URL y el valor será el diccionario con los datos
team_list = []
try:
    print("🌐 Cargando Sofascore...")
    driver.get("https://www.sofascore.com/es/football/tournament/world/world-championship/16#id:58210")
    
    # Esperamos a que cargue e interactúe la página
    time.sleep(2)
    print("📜 Haciendo scroll...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    print("🔍 Analizando tráfico de red y extrayendo datos...")
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
                    print(f"✅ Datos extraídos de {url} con claves: {claves}")
                    if "standings" in claves:
                        print("📊 Guardando clasificación...")
                        # Guardamos el diccionario usando la URL como identificador
                        with open("data/standings.json", "w", encoding="utf-8") as f:
                            json.dump(datos_diccionario, f, indent=4, ensure_ascii=False)
                        print("📋 Extrayendo datos de equipos para facilitar búsquedas futuras...")
                        team_list = teams.get_teams(datos_diccionario, store=True)
                        print(f"👥 Equipos extraídos: {[team.name for team in team_list]}")
                    elif "powerRankings" in claves:
                        print("📈 Guardando ranking de poder...")
                        with open("data/power_rankings.json", "w", encoding="utf-8") as f:
                            json.dump(datos_diccionario, f, indent=4, ensure_ascii=False)
                    elif "events" in claves:
                        print("📅 Guardando eventos programados...")
                        for evento in datos_diccionario["events"]:
                            local = evento["homeTeam"]["name"]
                            visitante = evento["awayTeam"]["name"]
                            print(f"   - {local} vs {visitante} el {evento['startTimestamp']}")
                            nombre_archivo = f"data/events/scheduled_event_{local} vs {visitante} el {evento['startTimestamp']}.json"
                            evento_limpio = events.clean_pre_event(evento)
                            apuestas = events.get_odds(evento["id"])
                            evento_limpio["odds"] = apuestas
                            with open(nombre_archivo, "w", encoding="utf-8") as f:
                                json.dump(evento_limpio, f, indent=4, ensure_ascii=False)
                    
                        
                except Exception as e:
                    # Algunas peticiones (como respuestas 204 o pendientes) no tienen contenido y darán error aquí.
                    # Las ignoramos de forma segura.
                    print(f"⚠️ No se pudo obtener el cuerpo de la respuesta para {url}: {e}")

except Exception as e:
    print(f"❌ Ocurrió un error general: {e}")

for team in team_list:
    print(f"📊 Obteniendo estadísticas recientes para {team.name}...")
    team.get_team_recent_performance(store=True)
    print(f"📋 Obteniendo últimos partidos para {team.name}...")
    team.get_team_last_matches(store=True)
    print(f"👥 Obteniendo plantilla de {team.name}...")
    squad = team.get_team_squad(store=True)
    team_seasons = team.get_team_seasons(store=True)
    for tournament_name, tournament_data in team_seasons.items():
        tournament_id = tournament_data["tournament_id"]
        for season in tournament_data["seasons"]:
            season_id = season["season_id"]
            season_year = season["season_year"]
            print(f"📈 Obteniendo estadísticas para {team.name} en {tournament_name} - {season['season_name']}...")
            team.get_team_stats(tournament_id, tournament_name, season_id, season['season_name'], season_year, store=True)
    for player in squad:
        print(f"👤 Obteniendo estadísticas para el jugador {player.name}...")
        player_obj = players.Player(player.player_id, player.name)
        player_obj.get_player_total_stats(store=True)

