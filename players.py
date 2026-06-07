import utils.sofascore_client
import utils.folder_maker
import urls
import json

class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self.data_folder = utils.folder_maker.create_data_folders(f"data/players/{self.player_id}_{self.name}")
        self.client = utils.sofascore_client.SofascoreClient()

    def get_player_seasons(self, store=False):
        url = urls.PLAYER_SEASONS.format(player_id=self.player_id)
        if store:
            seasons_data = self.client.get(url)
            with open(f"{self.data_folder}seasons.json", "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, indent=4, ensure_ascii=False)
            return seasons_data
        return self.client.get(url)

    def get_player_season_stats(self, tournament_id, tournament_name, season_id, season_name, store=False):
        url = urls.PLAYER_SEASON_STATS.format(player_id=self.player_id, tournament_id=tournament_id, season_id=season_id)
        try:
            player_stats = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas para {self.name} en {tournament_name} - {season_name}")
            player_stats = None
            store = False  # No tiene sentido guardar un archivo sin datos, así que desactivamos el guardado en caso de error
        if store:
            with open(f"{self.data_folder}tournament_{tournament_id}_{tournament_name}_season_{season_id}_{season_name.replace('/', '-')}.json", "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)
        return player_stats

    def get_player_total_stats(self, store=False):
        player_seasons = self.get_player_seasons()
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

    def get_player_stats_by_natural_year(self, year):
        pass

    def get_player_stats_by_season(self, season_name):
        pass

    def get_player_stats_by_tournament(self, tournament_name):
        pass

    def get_player_stats_by_tournament_and_season(self, tournament_name, season_name):
        pass

    def get_player_stats_by_league_adjusted(self, league_name):
        pass