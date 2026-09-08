"""ECS JSON logging for the dynamic_rendering package."""

from __future__ import annotations

import logging

import ecs_logging

SERVICE_NAME = "dynamic-rendering"
_LOGGER_ROOT = "app.dynamic_rendering"


def _configure_package_logger() -> logging.Logger:
    pkg_logger = logging.getLogger(_LOGGER_ROOT)
    if pkg_logger.handlers:
        return pkg_logger

    pkg_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        ecs_logging.StdlibFormatter(
            extra={"service": {"name": SERVICE_NAME}},
        )
    )
    pkg_logger.addHandler(handler)
    pkg_logger.propagate = False
    return pkg_logger


logger = _configure_package_logger()
