"""
logger.py
----------
Centralized logging utility for the MNAV macropad project.
"""

import logging
import os

def setup_logger(name: str) -> logging.Logger:
    """Create and configure a consistent logger for the MNAV project."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Avoid duplicate handlers when re-importing in PyQt
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
