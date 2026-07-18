"""
Centralized logging configuration for the application.
"""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logging with a clean, readable format.
    Call this once, at application startup (see app/main.py).
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if configure_logging() is called more than once
    # (e.g. during tests or auto-reload).
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers a little.
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("passlib").setLevel(logging.ERROR)
