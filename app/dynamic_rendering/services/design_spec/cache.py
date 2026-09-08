"""In-memory and on-disk cache for design token dicts (not cloneable XML)."""

from __future__ import annotations

import json
import os
from typing import Any

from app.dynamic_rendering.domain.models.design_spec import DesignSpec

_memory_cache: dict[str, DesignSpec] = {}


def memory_cache_get(key: str) -> DesignSpec | None:
    return _memory_cache.get(key)


def memory_cache_set(key: str, spec: DesignSpec) -> None:
    _memory_cache[key] = spec


def load_disk_tokens(cache_file: str, file_hash: str) -> tuple[dict[str, Any] | None, str]:
    """Return (tokens, source) from .designspec.json if hash matches."""
    if not os.path.exists(cache_file):
        return None, "heuristic"
    try:
        with open(cache_file, "r", encoding="utf-8") as fh:
            disk = json.load(fh)
        if disk.get("hash") == file_hash and isinstance(disk.get("tokens"), dict):
            if "question_pill_fill" not in disk["tokens"]:
                return None, "heuristic"
            return disk["tokens"], disk.get("source", "cached")
    except (OSError, json.JSONDecodeError):
        pass
    return None, "heuristic"


def save_disk_tokens(cache_file: str, file_hash: str, tokens: dict[str, Any], source: str) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as fh:
            json.dump({"hash": file_hash, "tokens": tokens, "source": source}, fh, indent=2)
    except OSError:
        pass
