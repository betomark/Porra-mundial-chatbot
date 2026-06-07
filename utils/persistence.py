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
    save_json_flag: bool = True,
    save_mongo_flag: bool = True,
    filter_fields: Optional[list] = None,
    upsert: bool = True,
) -> Dict[str, Any]:
    """Persist data to JSON file, MongoDB, or both.

    - If `save_json_flag` is True and `json_path` is provided, `json_data` (or `mongo_doc` if json_data is None)
      will be saved to `json_path` using `utils.json_store.save_json`.
    - If `save_mongo_flag` is True and `collection` and `mongo_doc` are provided, the document will be saved to MongoDB
      using `MongoDBClient.save_document`.

    Returns a dict with results for json and mongo operations.
    """
    res = {"json": None, "mongo": None}

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
