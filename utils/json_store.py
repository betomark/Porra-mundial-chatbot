import os
import json
import logging
from pathlib import Path

from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def save_json(path: str, data, indent: int = 4, ensure_dir: bool = True, ensure_ascii: bool = False):
    """Save `data` as JSON to `path`. Ensures parent directory exists when `ensure_dir` is True.

    Returns the path written to.
    """
    try:
        p = Path(path)
        if ensure_dir:
            p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        logger.info("Saved JSON to %s", str(p))
        return str(p)
    except Exception as e:
        logger.exception("Failed to save JSON to %s: %s", path, e)
        raise
