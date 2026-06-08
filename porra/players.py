from datafc.utils import SofascoreClient
import utils.folder_maker
from porra import urls
import json
import logging
from utils.logging_config import setup_logging
from utils.mongo_client import MongoDBClient
from utils.json_store import save_json
from utils.persistence import persist

setup_logging()
logger = logging.getLogger(__name__)

class Player:
    """Represents a player and provides methods for loading player statistics."""
    def __init__(self, player_id, name):
        """Initialize the Player instance with the player ID and name."""
        logger.debug("Creating Player instance: %s (%s)", name, player_id)
        self.player_id = player_id
        self.name = name
        self.mongo = MongoDBClient()
        self.data_folder = utils.folder_maker.create_data_folders(f"data/players/{self.player_id}_{self.name}")
        self.client = SofascoreClient()

    def get_player_seasons(self, store=False):
        """Fetch season information for the player from SofaScore."""
        logger.debug("Fetching seasons for player %s", self.name)
        url = urls.PLAYER_SEASONS.format(player_id=self.player_id)
        try:
            seasons_data = self.client.get(url)
            logger.info("Fetched seasons for player %s", self.name)
        except Exception as e:
            logger.error("Failed to fetch seasons for player %s: %s", self.name, e)
            seasons_data = None
            store = False  # It does not make sense to save a file without data, so disable storage on error

        if store:
            output_path = f"{self.data_folder}seasons.json"
            logger.info("Saving player seasons for %s to %s", self.name, output_path)
            persist(
                collection="player_seasons",
                mongo_doc={
                    "_id": self.player_id,
                    "player_id": self.player_id,
                    "player_name": self.name,
                    "seasons_data": seasons_data,
                },
                json_path=output_path,
                json_data=seasons_data,
                filter_fields=["_id"],
            )
        return seasons_data

    def get_player_season_stats(self, tournament_id, tournament_name, season_id, season_name, store=False):
        """Fetch statistics for a specific player season."""
        logger.debug("Fetching season stats for %s in %s - %s", self.name, tournament_name, season_name)
        url = urls.PLAYER_SEASON_STATS.format(player_id=self.player_id, tournament_id=tournament_id, season_id=season_id)
        try:
            player_stats = self.client.get(url)
            logger.info("Fetched season stats for %s in %s - %s", self.name, tournament_name, season_name)
        except Exception as e:
            logger.error("Failed to fetch season stats for %s in %s - %s: %s", self.name, tournament_name, season_name, e)
            player_stats = None
            store = False  # It does not make sense to save a file without data, so disable storage on error
        if store:
            output_path = f"{self.data_folder}tournament_{tournament_id}_{tournament_name}_season_{season_id}_{season_name.replace('/', '-')}.json"
            logger.info("Saving player season stats to %s", output_path)
            persist(
                collection="player_stats",
                mongo_doc={
                    "_id": f"{self.player_id}_{tournament_id}_{season_id}",
                    "player_id": self.player_id,
                    "player_name": self.name,
                    "tournament_id": tournament_id,
                    "tournament_name": tournament_name,
                    "season_id": season_id,
                    "season_name": season_name,
                    "season_year": player_stats.get("season_year"),
                    "stats": player_stats,
                },
                json_path=output_path,
                json_data=player_stats,
                filter_fields=["_id"],
            )
        return player_stats

    def get_player_total_stats(self, store=False):
        """Aggregate total statistics across all seasons for the player."""
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
            persist(
                collection="player_total_stats",
                mongo_doc={
                    "_id": self.player_id,
                    "player_id": self.player_id,
                    "player_name": self.name,
                    "total_stats": player_stats,
                },
                json_path=output_path,
                json_data=player_stats,
                filter_fields=["_id"],
            )

        logger.info("Total stats fetched for %s", self.name)
        return player_stats
    
    def get_player_context(self):
        """Placeholder for building a player-specific context payload."""
        logger.debug("get_player_context called for %s", self.name)
        logger.warning("get_player_context is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_natural_year(self, year):
        """Placeholder for retrieving player stats by calendar year."""
        logger.debug("get_player_stats_by_natural_year called for %s year=%s", self.name, year)
        logger.warning("get_player_stats_by_natural_year is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_season(self, season_name):
        """Placeholder for retrieving player stats filtered by season."""
        logger.debug("get_player_stats_by_season called for %s season_name=%s", self.name, season_name)
        logger.warning("get_player_stats_by_season is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_tournament(self, tournament_name):
        """Placeholder for retrieving player stats filtered by tournament."""
        logger.debug("get_player_stats_by_tournament called for %s tournament_name=%s", self.name, tournament_name)
        logger.warning("get_player_stats_by_tournament is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_tournament_and_season(self, tournament_name, season_name):
        """Placeholder for retrieving player stats filtered by tournament and season."""
        logger.debug("get_player_stats_by_tournament_and_season called for %s tournament_name=%s season_name=%s", self.name, tournament_name, season_name)
        logger.warning("get_player_stats_by_tournament_and_season is not implemented yet for %s", self.name)
        return None

    def get_player_stats_by_league_adjusted(self, league_name):
        """Placeholder for retrieving player stats adjusted by league strength."""
        logger.debug("get_player_stats_by_league_adjusted called for %s league_name=%s", self.name, league_name)
        logger.warning("get_player_stats_by_league_adjusted is not implemented yet for %s", self.name)
        return None
