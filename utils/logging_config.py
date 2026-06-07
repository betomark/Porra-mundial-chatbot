import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='application.log', level=logging.INFO):
    """
    Sets up the logging configuration for the application.

    Args:
        log_file (str): The name of the log file.
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
    """
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_path = os.path.join(log_directory, log_file)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers to prevent duplicate logs in reloads
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler - Rotates logs after 1MB, keeps 5 backup files
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logging.info(f"Logging configured. Log file: {log_path}, Level: {logging.getLevelName(level)}")

if __name__ == '__main__':
    setup_logging(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
