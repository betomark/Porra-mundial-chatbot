import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from utils.logging_config import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None

    def __new__(cls):
        """Asegura que solo exista una conexión activa (Patrón Singleton)"""
        if cls._instance is None:
            logger.debug("Initializing new MongoDBClient singleton instance.")
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGO_DB_NAME", "porra_db")
            logger.info("Connecting to MongoDB at %s using database %s", uri, db_name)
            cls._instance.client = MongoClient(uri)
            cls._instance.db = cls._instance.client[db_name]
        else:
            logger.debug("Reusing existing MongoDBClient singleton instance.")
        return cls._instance

    @property
    def database(self):
        logger.debug("Accessing MongoDB database property.")
        return self.db