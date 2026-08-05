"""Process-level logging composition."""

from __future__ import annotations

import logging

from app.config.settings import Settings
from app.logs.formatter import JsonLogFormatter

_HANDLER_MARKER = "_forgesight_json_handler"


def configure_logging(settings: Settings) -> None:
    """Install one structured stdout handler and align framework logger levels."""

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    formatter = JsonLogFormatter(
        service=settings.service_name,
        environment=settings.environment.value,
    )
    json_handler = next(
        (handler for handler in root_logger.handlers if getattr(handler, _HANDLER_MARKER, False)),
        None,
    )
    if json_handler is None:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        setattr(handler, _HANDLER_MARKER, True)
        root_logger.addHandler(handler)
    else:
        json_handler.setFormatter(formatter)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).setLevel(settings.log_level)
