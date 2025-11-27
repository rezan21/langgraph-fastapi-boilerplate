import logging
import logging.config
import os
import sys
from typing import Optional


_IS_CONFIGURED: bool = False


def _resolve_log_level(default: str = "INFO") -> str:
    level = os.getenv("LOG_LEVEL", default).upper()
    # Validate level; fall back to default on invalid input
    if level not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}:
        return default
    return level


def configure_logging(force: bool = False) -> None:
    """Configure application-wide logging.

    Reads LOG_LEVEL from environment (default INFO). Designed to play nicely with
    uvicorn by not disabling existing loggers and explicitly configuring
    uvicorn loggers to use the same console handler.
    """
    global _IS_CONFIGURED
    if _IS_CONFIGURED and not force:
        return

    log_level = _resolve_log_level()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "console",
            }
        },
        "root": {"level": log_level, "handlers": ["console"]},
        # Align uvicorn loggers with our console handler without double-propagation
        "loggers": {
            "uvicorn": {"level": log_level, "handlers": ["console"], "propagate": False},
            "uvicorn.error": {"level": log_level, "handlers": ["console"], "propagate": False},
            "uvicorn.access": {"level": log_level, "handlers": ["console"], "propagate": False},
        },
    }

    logging.config.dictConfig(logging_config)
    _IS_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-specific logger, ensuring logging is configured.

    Example:
        from logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello")
    """
    # Ensure configuration has been applied, especially in non-uvicorn contexts
    if not _IS_CONFIGURED and not logging.getLogger().handlers:
        # If the root logger has no handlers, apply our config
        configure_logging()

    return logging.getLogger(name if name else __name__)


# Configure at import time for scripts and background tasks. In uvicorn, this
# will harmonize handlers/levels without disabling existing loggers.
configure_logging()


