"""Self-contained template conversion pipeline (drop-in module)."""

import app.dynamic_rendering.log as _log  # noqa: F401 — configure ECS logging

from app.dynamic_rendering.services.orchestrator import build_deck

__all__ = ["build_deck"]
