import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDBClient:
    _instance = None

    def __new__(cls):
        """Asegura que solo exista una conexión activa (Patrón Singleton)"""
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGO_DB_NAME", "porra_db")
            
            cls._instance.client = MongoClient(uri)
            cls._instance.db = cls._instance.client[db_name]
        return cls._instance

    @property
    def database(self):
        return self.db