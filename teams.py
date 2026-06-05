import json
import utils.sofascore_client
import urls

def get_teams(standings_dict):
    datos_equipos = {}
    for grupo in standings_dict["standings"]:
        for equipo in grupo["rows"]:
            datos_equipos[equipo["team"]["name"]] = equipo["team"]["id"]

    with open("data/teams.json", "w", encoding="utf-8") as f:
        json.dump(datos_equipos, f, indent=4, ensure_ascii=False)

def get_team_stats(team_id):
    url = urls.TEAM_STATS.format(team_id=team_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    return sofascore_client.get(url)

def get_team_recent_performance(team_id):
    url = urls.TEAM_RECENT_PERFORMANCE.format(team_id=team_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    return sofascore_client.get(url)

def get_team_last_matches(team_id):
    url = urls.TEAM_LASTS_MATCHES.format(team_id=team_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    return sofascore_client.get(url)

def get_team_squad(team_id):
    url = urls.SQUAD.format(team_id=team_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    return sofascore_client.get(url)