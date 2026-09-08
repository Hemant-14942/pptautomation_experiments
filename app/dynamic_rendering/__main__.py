"""CLI entry: python -m app.dynamic_rendering input.pptx template.pptx output.pptx"""

from __future__ import annotations

import logging
import sys

import app.dynamic_rendering.log  # noqa: F401 — configure ECS logging

from app.dynamic_rendering.services.orchestrator import build_deck

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 3:
        logger.error("invalid CLI usage")
        print("Usage: python -m app.dynamic_rendering <input.pptx> <template.pptx> <output.pptx>")
        return 1
    build_deck(args[0], args[1], args[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
