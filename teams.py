import json
import logging
from datafc.utils import sofascore_client
import utils.folder_maker
import urls
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
import players

def get_teams(standings_dict, store=False):
    logger.debug("Starting get_teams with store=%s", store)
    datos_equipos = {}
    teams = []
    for grupo in standings_dict["standings"]:
        for equipo in grupo["rows"]:
            team_id = equipo["team"]["id"]
            team_name = equipo["team"]["name"]
            datos_equipos[team_name] = team_id
            teams.append(Team(team_id, team_name))

    if store:
        logger.info("Storing team list to data/teams.json")
        with open("data/teams.json", "w", encoding="utf-8") as f:
            json.dump(datos_equipos, f, indent=4, ensure_ascii=False)
    logger.info("Finished get_teams with %d teams", len(teams))
    return teams
class Team:
    def __init__(self, team_id, name):
        logger.debug("Creating Team instance: %s (%s)", name, team_id)
        self.team_id = team_id
        self.name = name
        self.player_list = []
        self.client = sofascore_client.SofascoreClient()
        self.data_folder = utils.folder_maker.create_data_folders(f"data/teams/{self.team_id}_{self.name}")

    def get_team_seasons(self, store=False):
        logger.debug("Fetching team seasons for %s", self.name)
        url = urls.TEAM_SEASONS.format(team_id=self.team_id)
        response = self.client.get(url)
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
            logger.info("Saving seasons for %s to %sseasons.json", self.name, self.data_folder)
            with open(f"{self.data_folder}seasons.json", "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, indent=4, ensure_ascii=False)
        logger.info("Retrieved %d tournaments for team %s", len(seasons_data), self.name)
        return seasons_data

    def get_team_stats(self, tournament_id, tournament_name, season_id, season_name, season_year, store=False):
        logger.debug("Fetching stats for %s in %s - %s", self.name, tournament_name, season_name)
        url = urls.TEAM_STATS.format(team_id=self.team_id, tournament_id=tournament_id, season_id=season_id)
        
        team_stats = {"tournament_id": tournament_id, "tournament_name": tournament_name, "season_id": season_id, "season_name": season_name, "season_year": season_year, "stats": {}}
        try:
            response = self.client.get(url)
            team_stats["stats"] = response
            logger.info("Fetched stats for %s in %s - %s", self.name, tournament_name, season_name)
        except Exception as e:
            logger.error("Failed to fetch stats for %s in %s - %s: %s", self.name, tournament_name, season_name, e)
            team_stats["stats"] = None
            store = False  # No tiene sentido guardar un archivo sin datos, así que desactivamos el guardado en caso de error
        if store:
            output_path = f"{self.data_folder}tournament_{tournament_id}_{tournament_name}_season_{season_id}_{season_name.replace('/', '-')}.json"
            logger.info("Saving team stats to %s", output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(team_stats, f, indent=4, ensure_ascii=False)
        return team_stats

    def get_team_recent_performance(self, store=False):
        logger.debug("Fetching recent performance for %s", self.name)
        url = urls.TEAM_RECENT_PERFORMANCE.format(team_id=self.team_id)
        if store:
            performance_data = self.client.get(url)
            output_path = f"{self.data_folder}performance.json"
            logger.info("Saving recent performance for %s to %s", self.name, output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(performance_data, f, indent=4, ensure_ascii=False)
            return performance_data
        return self.client.get(url)

    def get_team_last_matches(self, store=False):
        logger.debug("Fetching last matches for %s", self.name)
        url = urls.TEAM_LASTS_MATCHES.format(team_id=self.team_id)
        if store:
            matches_data = self.client.get(url)
            output_path = f"{self.data_folder}last_matches.json"
            logger.info("Saving last matches for %s to %s", self.name, output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(matches_data, f, indent=4, ensure_ascii=False)
            return matches_data
        return self.client.get(url)

    def get_team_squad(self, store=False):
        logger.debug("Fetching squad for %s", self.name)
        url = urls.SQUAD.format(team_id=self.team_id)
        player_list = []
        squad_data = self.client.get(url)
        if store:
            output_path = f"{self.data_folder}squad.json"
            logger.info("Saving squad for %s to %s", self.name, output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(squad_data, f, indent=4, ensure_ascii=False)
        for player in squad_data["players"]:
            player_list.append(players.Player(player['player']["id"], player['player']["name"]))
        self.player_list = player_list
        logger.info("Retrieved %d players for %s", len(self.player_list), self.name)
        return self.player_list
    
    def get_squad_context(self):
        logger.debug("Building squad context for %s", self.name)
        squad_data = self.get_team_squad()
        squad_context = {}
        for player in squad_data["players"]:
            player_id = player["id"]
            player_name = player["name"]
            player_stats = players.Player(player_id).get_player_total_stats()
            squad_context[player_name] = {
                "player_id": player_id,
                "stats": player_stats
            }
        logger.info("Squad context built for %s", self.name)
        return squad_context
    
    def get_team_context(self, tournament_id, season_id):
        logger.debug("Assembling full team context for %s", self.name)
        context = {
            "stats": self.get_team_stats(tournament_id, season_id),
            "performance": self.get_team_recent_performance(),
            "last_matches": self.get_team_last_matches(),
            "squad": self.get_squad_context()
        }
        logger.info("Full team context assembled for %s", self.name)
        return context