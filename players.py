from datafc.utils import sofascore_client
import utils.folder_maker
import urls
import json
import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, player_id, name):
        logger.debug("Creating Player instance: %s (%s)", name, player_id)
        self.player_id = player_id
        self.name = name
        self.data_folder = utils.folder_maker.create_data_folders(f"data/players/{self.player_id}_{self.name}")
        self.client = sofascore_client.SofascoreClient()

    def get_player_seasons(self, store=False):
        logger.debug("Fetching seasons for player %s", self.name)
        url = urls.PLAYER_SEASONS.format(player_id=self.player_id)
        if store:
            seasons_data = self.client.get(url)
            output_path = f"{self.data_folder}seasons.json"
            logger.info("Saving player seasons for %s to %s", self.name, output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, indent=4, ensure_ascii=False)
            return seasons_data
        return self.client.get(url)

    def get_player_season_stats(self, tournament_id, tournament_name, season_id, season_name, store=False):
        logger.debug("Fetching season stats for %s in %s - %s", self.name, tournament_name, season_name)
        url = urls.PLAYER_SEASON_STATS.format(player_id=self.player_id, tournament_id=tournament_id, season_id=season_id)
        try:
            player_stats = self.client.get(url)
            logger.info("Fetched season stats for %s in %s - %s", self.name, tournament_name, season_name)
        except Exception as e:
            logger.error("Failed to fetch season stats for %s in %s - %s: %s", self.name, tournament_name, season_name, e)
            player_stats = None
            store = False  # No tiene sentido guardar un archivo sin datos, así que desactivamos el guardado en caso de error
        if store:
            output_path = f"{self.data_folder}tournament_{tournament_id}_{tournament_name}_season_{season_id}_{season_name.replace('/', '-')}.json"
            logger.info("Saving player season stats to %s", output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)
        return player_stats

    def get_player_total_stats(self, store=False):
        logger.debug("Fetching total stats for player %s", self.name)
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
            output_path = f"{self.data_folder}total_stats.json"
            logger.info("Saving total stats for %s to %s", self.name, output_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4, ensure_ascii=False)

        logger.info("Total stats fetched for %s", self.name)
        return player_stats
    
    def get_player_context(self):
        logger.debug("get_player_context called for %s", self.name)
        logger.warning("get_player_context is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_natural_year(self, year):
        logger.debug("get_player_stats_by_natural_year called for %s year=%s", self.name, year)
        logger.warning("get_player_stats_by_natural_year is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_season(self, season_name):
        logger.debug("get_player_stats_by_season called for %s season_name=%s", self.name, season_name)
        logger.warning("get_player_stats_by_season is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_tournament(self, tournament_name):
        logger.debug("get_player_stats_by_tournament called for %s tournament_name=%s", self.name, tournament_name)
        logger.warning("get_player_stats_by_tournament is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_tournament_and_season(self, tournament_name, season_name):
        logger.debug("get_player_stats_by_tournament_and_season called for %s tournament_name=%s season_name=%s", self.name, tournament_name, season_name)
        logger.warning("get_player_stats_by_tournament_and_season is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_league_adjusted(self, league_name):
        logger.debug("get_player_stats_by_league_adjusted called for %s league_name=%s", self.name, league_name)
        logger.warning("get_player_stats_by_league_adjusted is not implemented yet for %s", self.name)
        return None