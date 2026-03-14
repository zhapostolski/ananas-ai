from __future__ import annotations

import logging
import os
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured logger for the given module name."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger
