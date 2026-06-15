"""
Utility helpers: simple logging helpers used across modules.
"""
from __future__ import annotations
import logging
import os

def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

setup_logging()
logger = logging.getLogger("omniagent")
