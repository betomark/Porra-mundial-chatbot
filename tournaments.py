import json
import logging
from datafc.utils import sofascore_client
import utils.folder_maker
import urls
from utils.logging_config import setup_logging
from utils.mongo_client import MongoDBClient
from utils.json_store import save_json
from utils.persistence import persist

setup_logging()
logger = logging.getLogger(__name__)

class Tournament:
    def __init__(self, tournament_id, name):
        logger.debug("Creating Tournament instance: %s (%s)", name, tournament_id)
        self.tournament_id = tournament_id
        self.name = name
        self.mongo = MongoDBClient()
        self.data_folder = utils.folder_maker.create_data_folders(f"data/tournaments/{self.tournament_id}_{self.name}")
        self.client = sofascore_client.SofascoreClient()

    def get_tournament_seasons(self, store=False):
        logger.debug("Fetching tournament seasons for %s", self.name)
        url = urls.TOURNAMENT_SEASONS.format(tournament_id=self.tournament_id)
        response = self.client.get(url)
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
            output_path = f"{self.data_folder}seasons.json"
            logger.info("Saving tournament seasons for %s to %s", self.name, output_path)
            persist(
                collection="tournament_seasons",
                mongo_doc={
                    "_id": self.tournament_id,
                    "tournament_id": self.tournament_id,
                    "tournament_name": self.name,
                    "seasons": seasons_data,
                },
                json_path=output_path,
                json_data=seasons_data,
                filter_fields=["_id"],
            )
        logger.info("Retrieved %d seasons for tournament %s", len(seasons_data), self.name)
        return seasons_data

    def get_tournament_stats(self, season_id, season_name, season_year, store=False):
        logger.debug("Fetching stats for tournament %s season %s", self.name, season_name)
        url = urls.TOURNAMENT_STATS.format(tournament_id=self.tournament_id, season_id=season_id)
        team_stats = None
        try:
            team_stats = self.client.get(url)
            logger.info("Fetched stats for tournament %s season %s", self.name, season_name)
        except Exception as e:
            logger.error("Failed to fetch stats for %s - %s: %s", self.name, season_name, e)
        if store and team_stats is not None:
            output_path = f"{self.data_folder}stats_{season_id}_{season_name.replace('/', '-')}.json"
            logger.info("Saving tournament stats for %s season %s to %s", self.name, season_name, output_path)
            persist(
                collection="tournament_stats",
                mongo_doc={
                    "_id": f"{self.tournament_id}_{season_id}",
                    "tournament_id": self.tournament_id,
                    "tournament_name": self.name,
                    "season_id": season_id,
                    "season_name": season_name,
                    "season_year": season_year,
                    "stats": team_stats,
                },
                json_path=output_path,
                json_data=team_stats,
                filter_fields=["_id"],
            )
        return team_stats
