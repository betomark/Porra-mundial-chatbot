from datafc.utils._client import SofascoreClient
import utils.folder_maker
import urls
import json
from default_dicts import PLAYER_DEFAULT_STATS

class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self.teams = []  # Lista de equipos en los que ha jugado el jugador, con formato {"team_id": ..., "team_name": ..., "tournament_id": ..., "tournament_name": ..., "season_id": ..., "season_name": ...}
        self.data_folder = utils.folder_maker.create_data_folders(f"data/players/{self.name}_{self.player_id}")
        self.client = SofascoreClient()

    def get_player_seasons(self, store=False):
        url = urls.PLAYER_SEASONS.format(player_id=self.player_id)
        try:
            print(f"Obteniendo temporadas para el jugador {self.name}...")
            seasons_data = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las temporadas para el jugador {self.name}")
            return None
        if store:
            with open(f"{self.data_folder}seasons.json", "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, indent=4, ensure_ascii=False)
        return seasons_data

    def get_player_season_stats(self, tournament_id, tournament_name, season_id, season_name, store=False):
        url = urls.PLAYER_SEASON_STATS.format(player_id=self.player_id, tournament_id=tournament_id, season_id=season_id)
        try:
            print(f"Obteniendo estadísticas para el jugador {self.name} en {tournament_name} - {season_name}...")
            player_stats = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas para {self.name} en {tournament_name} - {season_name}")
            return None
        if store:
            with open(f"{self.data_folder}tournament_{tournament_id}_{tournament_name}_season_{season_id}_{season_name.replace('/', '-')}.json", "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)
        return player_stats

    def get_player_total_stats(self, store=False):
        player_seasons = self.get_player_seasons()
        if player_seasons is None:
            print(f"⚠️ No se pudieron obtener las temporadas para el jugador {self.name}. No se pueden calcular las estadísticas totales.")
            return None
        player_stats = {}
        for tournament in player_seasons["uniqueTournamentSeasons"]:
            tournament_id = tournament["uniqueTournament"]["id"]
            tournament_name = tournament["uniqueTournament"]["name"]
            tournament_place = tournament["uniqueTournament"]["category"]["name"]
            player_stats[tournament_name] = {
                "tournament_id": tournament_id,
                "tournament_place": tournament_place,
                "seasons": {}
            }
            for season in tournament["seasons"]:
                season_id = season["id"]
                season_name = season["name"]
                season_year = season["year"]
                player_stats[tournament_name]["seasons"][season_name] = {
                    "season_id": season_id,
                    "season_year": season_year,
                    "stats": self.get_player_season_stats(tournament_id, tournament_name, season_id, season_name)
                }
        if store:
            with open(f"{self.data_folder}total_stats.json", "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)
        return player_stats
    
    def get_player_context(self):
        pass

    def get_player_stats_by_year(self, year, store=False):
        player_seasons = self.get_player_seasons()
        player_stats = {}
        for tournament in player_seasons["uniqueTournamentSeasons"]:
            for season in tournament["seasons"]:
                season_year = season["year"]
                if season_year == str(year) or season_year.split("/")[1] == str(year)[-2:]:
                    tournament_id = tournament["uniqueTournament"]["id"]
                    tournament_name = tournament["uniqueTournament"]["name"]
                    tournament_place = tournament["uniqueTournament"]["category"]["name"]
                    season_id = season["id"]
                    season_name = season["name"]
                    
                    player_stats[tournament_name] = {
                        "tournament_id": tournament_id,
                        "tournament_place": tournament_place,
                        "seasons": {}
                    }
                    player_stats[tournament_name]["seasons"][season_name] = {
                        "season_id": season_id,
                        "season_year": season_year,
                        "stats": self.get_player_season_stats(tournament_id, tournament_name, season_id, season_name)
                    }
        if store:
            with open(f"{self.data_folder}stats_year_{year}.json", "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)
        return player_stats

    def get_player_stats_summary_by_year(self, year, store=False):
        player_seasons = self.get_player_seasons()
        player_stats = PLAYER_DEFAULT_STATS.copy()
        for tournament in player_seasons["uniqueTournamentSeasons"]:
            for season in tournament["seasons"]:
                season_year = season["year"]
                if season_year == str(year) or season_year.split("/")[1] == str(year)[-2:]:
                    tournament_id = tournament["uniqueTournament"]["id"]
                    season_id = season["id"]
                    season_stats = self.get_player_season_stats(tournament_id, tournament_name, season_id, season_name)
                    for stat_key, stat_value in season_stats.items():
                        if stat_key == "rating":
                            pass
                        elif player_stats[stat_key] is None:
                            player_stats[stat_key] = stat_value
                        elif stat_key.contains("Percentage"):
                            player_stats[stat_key] += stat_value
                            player_stats[stat_key] /= 2
                        else:
                            player_stats[stat_key] += stat_value
        player_stats["rating"] = player_stats["totalRating"] / player_stats["countRating"] if player_stats["countRating"] > 0 else None
        if store:
            with open(f"{self.data_folder}stats_summary_year_{year}.json", "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)
        return player_stats

    def get_player_stats_by_tournament(self, tournament_name):
        pass

    def get_player_stats_by_tournament_and_season(self, tournament_name, season_name):
        pass

    def get_player_stats_by_league_adjusted(self, league_name):
        pass

def merge_player_summary_stats_by_year(player_stats_list):
    merged_stats = PLAYER_DEFAULT_STATS.copy()
    for player_stats in player_stats_list:
        for stat_key, stat_value in player_stats.items():
            if stat_key == "rating":
                pass
            elif merged_stats[stat_key] is None:
                merged_stats[stat_key] = stat_value
            elif stat_key.contains("Percentage"):
                merged_stats[stat_key] += stat_value
                merged_stats[stat_key] /= 2
            else:
                merged_stats[stat_key] += stat_value
    merged_stats["rating"] = merged_stats["totalRating"] / merged_stats["countRating"] if merged_stats["countRating"] > 0 else None
    return merged_stats