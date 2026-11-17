from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from recipescope.constants import LOG_DIR
from version import APP_NAME, VERSION


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    file_handler = RotatingFileHandler(
        LOG_DIR / "recipescope.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info("Starting %s v%s", APP_NAME, VERSION)
    return logger
