import os
import logging
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from utils.logging_config import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None

    def __new__(cls):
        """Ensure that only one active connection exists (Singleton pattern)."""
        if cls._instance is None:
            logger.debug("Initializing new MongoDBClient singleton instance.")
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGO_DB_NAME", "porra_db")
            logger.info("Connecting to MongoDB at %s using database %s", uri, db_name)
            cls._instance.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            cls._instance.db = cls._instance.client[db_name]
            try:
                cls._instance.client.admin.command("ping")
                logger.info("MongoDB connection successful")
            except Exception as e:
                logger.error("MongoDB connection failed: %s", e)
        else:
            logger.debug("Reusing existing MongoDBClient singleton instance.")
        return cls._instance

    @property
    def database(self):
        logger.debug("Accessing MongoDB database property.")
        return self.db

    def get_collection(self, collection_name):
        logger.debug("Retrieving MongoDB collection: %s", collection_name)
        return self.database[collection_name]

    def save_document(self, collection_name, document, filter_fields=None, upsert=True):
        """Save or update a document in MongoDB."""
        collection = self.get_collection(collection_name)
        document = dict(document)
        now = datetime.datetime.utcnow()
        document["updated_at"] = now

        if filter_fields is None:
            if "_id" in document:
                filter_query = {"_id": document["_id"]}
            else:
                logger.debug("Inserting new document into %s because no _id and no filter_fields were provided.", collection_name)
                result = collection.insert_one(document)
                logger.info("Inserted document into %s with generated _id=%s", collection_name, result.inserted_id)
                return result
        else:
            filter_query = {field: document[field] for field in filter_fields if field in document}
            if not filter_query:
                logger.warning("save_document called with empty filter_fields for collection %s; inserting a new document.", collection_name)
                result = collection.insert_one(document)
                logger.info("Inserted document into %s with generated _id=%s", collection_name, result.inserted_id)
                return result

        document.setdefault("created_at", now)
        if upsert:
            result = collection.update_one(filter_query, {"$set": document, "$setOnInsert": {"created_at": document["created_at"]}}, upsert=True)
            if getattr(result, "upserted_id", None):
                logger.info("Upserted document into %s with _id=%s", collection_name, result.upserted_id)
            else:
                logger.info("Updated document in %s matching %s", collection_name, filter_query)
            return result
        else:
            logger.debug("Inserting document into %s without upsert", collection_name)
            result = collection.insert_one(document)
            logger.info("Inserted document into %s with generated _id=%s", collection_name, result.inserted_id)
            return result

    def find_one(self, collection_name, query, projection=None):
        logger.debug("Finding one document in %s with query=%s", collection_name, query)
        collection = self.get_collection(collection_name)
        return collection.find_one(query, projection)

    def find_many(self, collection_name, query=None, projection=None, limit=100):
        query = query or {}
        logger.debug("Finding many documents in %s with query=%s limit=%s", collection_name, query, limit)
        collection = self.get_collection(collection_name)
        return list(collection.find(query, projection).limit(limit))

    def replace_document(self, collection_name, filter_query, document, upsert=False):
        logger.debug("Replacing document in %s matching %s", collection_name, filter_query)
        collection = self.get_collection(collection_name)
        result = collection.replace_one(filter_query, document, upsert=upsert)
        logger.info("Replaced document in %s matching %s; modified_count=%s", collection_name, filter_query, result.modified_count)
        return result