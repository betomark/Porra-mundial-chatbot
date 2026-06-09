import json
from datafc.utils._client import SofascoreClient
import utils.folder_maker
import urls
import players
import events

def get_teams(standings_dict, store=False):
    datos_equipos = {}
    teams = []
    for grupo in standings_dict["standings"]:
        for equipo in grupo["rows"]:
            team_id = equipo["team"]["id"]
            team_name = equipo["team"]["name"]
            datos_equipos[team_name] = team_id
            teams.append(Team(team_id, team_name))

    if store:
        with open("data/teams.json", "w", encoding="utf-8") as f:
            json.dump(datos_equipos, f, indent=4, ensure_ascii=False)
    return teams
class Team:
    def __init__(self, team_id, name):
        self.team_id = team_id
        self.name = name
        self.player_list = []
        self.client = SofascoreClient()
        self.data_folder = utils.folder_maker.create_data_folders(f"data/teams/{self.team_id}_{self.name}")

    def get_team_seasons(self, store=False):
        url = urls.TEAM_SEASONS.format(team_id=self.team_id)
        try:
            print(f"Obteniendo temporadas para {self.name}")
            response = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las temporadas para {self.name}")
            return None
        seasons_data = {}
        for tournament in response["uniqueTournamentSeasons"]:
            tournament_name = tournament["uniqueTournament"]["name"]
            tournament_id = tournament["uniqueTournament"]["id"]
            tournament_place = tournament["uniqueTournament"]["category"]["name"]
            seasons_data[tournament_name] = {
                "tournament_id": tournament_id,
                "tournament_place": tournament_place,
                "seasons": []
            }
            for season in tournament["seasons"]:
                season_name = season["name"]
                season_id = season["id"]
                season_year = season["year"]
                seasons_data[tournament_name]["seasons"].append({
                    "season_name": season_name,
                    "season_id": season_id,
                    "season_year": season_year
                })

        if store:
            with open(f"{self.data_folder}seasons.json", "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, indent=4, ensure_ascii=False)
            return seasons_data
        return seasons_data

    def get_team_stats(self, tournament_id, tournament_name, season_id, season_name, season_year, store=False, clean=False):
        url = urls.TEAM_STATS.format(team_id=self.team_id, tournament_id=tournament_id, season_id=season_id)
        print(f"Obteniendo estadísticas para {self.name} en {tournament_name} - {season_name} ({season_year})")
        team_stats = {"tournament_id": tournament_id, "tournament_name": tournament_name, "season_id": season_id, "season_name": season_name, "season_year": season_year, "stats": {}}
        try:
            response = self.client.get(url)
            team_stats["stats"] = response
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas para {self.name} en {tournament_name} - {season_name} ({season_year})")
            team_stats["stats"] = None
            store = False  # No tiene sentido guardar un archivo sin datos, así que desactivamos el guardado en caso de error
        if store:
            with open(f"{self.data_folder}tournament_{tournament_id}_{tournament_name}_season_{season_id}_{season_name.replace('/', '-')}.json", "w", encoding="utf-8") as f:
                json.dump(team_stats, f, indent=4, ensure_ascii=False)
        return team_stats

    def get_team_recent_performance(self, store=False, clean=False):
        url = urls.TEAM_RECENT_PERFORMANCE.format(team_id=self.team_id)
        try:
            print(f"Obteniendo estadísticas de rendimiento reciente para {self.name}")
            performance_data = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas de rendimiento reciente para {self.name}")
            return None
        if store:
            performance_data = self.client.get(url)
            with open(f"{self.data_folder}performance.json", "w", encoding="utf-8") as f:
                json.dump(performance_data, f, indent=4, ensure_ascii=False)
        return performance_data

    def get_team_last_matches(self, store=False, clean=False):
        url = urls.TEAM_LASTS_MATCHES.format(team_id=self.team_id)
        try:
            print(f"Obteniendo últimos partidos para {self.name}")
            matches_data = self.client.get(url)
            if clean:
                matches_data = [events.clean_past_event(match) for match in matches_data]
        except:
            print(f"⚠️ No se pudieron obtener los últimos partidos para {self.name}")
            return None
        if store:
            with open(f"{self.data_folder}last_matches.json", "w", encoding="utf-8") as f:
                json.dump(matches_data, f, indent=4, ensure_ascii=False)
        return matches_data

    def get_team_squad(self, store=False, clean=False):
        url = urls.SQUAD.format(team_id=self.team_id)
        player_list = []
        try:
            print(f"Obteniendo plantilla para {self.name}")
            squad_data = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las plantillas para {self.name}")
            return None
        if store:
            with open(f"{self.data_folder}squad.json", "w", encoding="utf-8") as f:
                json.dump(squad_data, f, indent=4, ensure_ascii=False)
        for player in squad_data["players"]:
            player_list.append(players.Player(player['player']["id"], player['player']["name"]))
        self.player_list = player_list
        return self.player_list
    
    def get_squad_context(self):
        squad_data = self.get_team_squad()
        squad_context = {}
        for player in squad_data["players"]:
            player_id = player["id"]
            player_name = player["name"]
            print(f"Obteniendo estadísticas para {player_name}")
            player_stats = players.Player(player_id).get_player_total_stats()
            squad_context[player_name] = {
                "player_id": player_id,
                "stats": player_stats
            }
        return squad_context
    
    def get_team_context(self, tournament_id, season_id):
        context = {
            "stats": self.get_team_stats(tournament_id, season_id),
            "performance": self.get_team_recent_performance(),
            "last_matches": self.get_team_last_matches(),
            "squad": self.get_squad_context()
        }
        return context