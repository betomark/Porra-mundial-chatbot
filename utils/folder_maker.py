import os
import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def create_data_folders(folder_path):
    logger.debug("Ensuring data folder exists at %s", folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info("Created folder path: %s", folder_path)
    else:
        logger.debug("Folder path already exists: %s", folder_path)
    return folder_path + "/"
