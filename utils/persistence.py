import os
import logging
from typing import Optional, Any, Dict

from utils.json_store import save_json
from utils.mongo_client import MongoDBClient
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def persist(
    collection: Optional[str] = None,
    mongo_doc: Optional[Dict[str, Any]] = None,
    json_path: Optional[str] = None,
    json_data: Optional[Any] = None,
    save_json_flag: Optional[bool] = None,
    save_mongo_flag: Optional[bool] = None,
    filter_fields: Optional[list] = None,
    upsert: bool = True,
) -> Dict[str, Any]:
    """Persist data to JSON file, MongoDB, or both.

    Behavior defaults may be controlled using the environment variable `PERSIST_DEFAULT`:
      - `json`  -> only save JSON files
      - `mongo` -> only save to MongoDB
      - `both`  -> save to both (default)

    If `save_json_flag` or `save_mongo_flag` are provided (not None), they override the environment default.

    Returns a dict with results for json and mongo operations.
    """
    res = {"json": None, "mongo": None}

    # Determine defaults from environment when flags are not explicitly provided
    env_default = os.getenv("PERSIST_DEFAULT", "both").lower()
    if env_default == "json":
        default_json, default_mongo = True, False
    elif env_default == "mongo":
        default_json, default_mongo = False, True
    else:
        default_json, default_mongo = True, True

    if save_json_flag is None:
        save_json_flag = default_json
    if save_mongo_flag is None:
        save_mongo_flag = default_mongo

    if save_json_flag and json_path:
        try:
            data_to_write = json_data if json_data is not None else mongo_doc
            if data_to_write is None:
                logger.warning("persist called with save_json_flag=True but no data provided for %s", json_path)
            else:
                path = save_json(json_path, data_to_write)
                res["json"] = {"path": path}
        except Exception as e:
            res["json"] = {"error": str(e)}

    if save_mongo_flag and collection and mongo_doc is not None:
        try:
            mongo = MongoDBClient()
            result = mongo.save_document(collection, mongo_doc, filter_fields=filter_fields, upsert=upsert)
            res["mongo"] = {"result": str(getattr(result, "raw_result", result))}
        except Exception as e:
            res["mongo"] = {"error": str(e)}

    return res
