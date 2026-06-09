import json
from datafc.utils._client import SofascoreClient
import utils.folder_maker
import urls

class Tournament:
    def __init__(self, tournament_id, name, season_id=None, season_name=None):
        self.tournament_id = tournament_id
        self.name = name
        self.season_id = season_id
        self.season_name = season_name
        self.data_folder = utils.folder_maker.create_data_folders(f"data/tournaments/{self.tournament_id}_{self.name}")
        self.client = SofascoreClient()

    def get_tournament_seasons(self, store=False):
        url = urls.TOURNAMENT_SEASONS.format(tournament_id=self.tournament_id)
        try:
            print(f"Obteniendo temporadas para el torneo {self.name}")
            response = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las temporadas para {self.name}")
            return None
        seasons_data = {}
        for season in response["seasons"]:
            season_name = season["name"]
            season_id = season["id"]
            season_year = season["year"]
            seasons_data[season_name] = {
                "season_id": season_id,
                "season_year": season_year
            }
        if store:
            with open(f"{self.data_folder}seasons.json", "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, indent=4, ensure_ascii=False)
        return seasons_data

    def get_tournament_stats(self, season_id, season_name, season_year, store=False):
        url = urls.TOURNAMENT_STATS.format(tournament_id=self.tournament_id, season_id=season_id)
        try:
            print(f"Obteniendo estadísticas para el torneo {self.name} - {season_name}...")
            team_stats = self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas para {self.name} - {season_name}")
            return None
        if store:
            with open(f"{self.data_folder}season_{season_id}_{season_name.replace('/', '-')}.json", "w", encoding="utf-8") as f:
                json.dump(team_stats, f, indent=4, ensure_ascii=False)
        return team_stats
    
    def get_tournament_season_standings(self, season_id=None):
        pass

    def get_tournament_season_teams(self, season_id=None):
        pass

    def get_tournament_season_upcoming_events(self, season_id=None):
        pass

    def get_tournament_season_past_events(self, season_id=None):
        pass

    def get_tournament_season_events(self, season_id):
        pass

    def get_power_ranking_rounds(self, season_id):
        url = urls.POWER_RANKINGS_ROUNDS.format(tournament_id=self.tournament_id, season_id=season_id)
        print(url)
        try:
            return self.client.get(url)
        except:
            print(f"⚠️ No se pudieron obtener las estadísticas para {self.name} ")
            return None