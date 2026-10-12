import logging
import logging.config

from app.core.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""

    log_level = settings.log_level.upper()

    if log_level not in {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }:
        log_level = "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": ("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the specified module."""

    return logging.getLogger(name)


# Configure logging when this module is imported.
setup_logging()
