"""Public entry: get_design_spec(template_path)."""

from __future__ import annotations

import hashlib
import logging
import os
import zipfile
from io import BytesIO

from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.design_spec.cache import (
    load_disk_tokens,
    memory_cache_get,
    memory_cache_set,
    save_disk_tokens,
)
from app.dynamic_rendering.services.design_spec.scanner import scan_template
from app.dynamic_rendering.services.design_spec.token_builder import spec_from_tokens_and_scan
from app.dynamic_rendering.services.style_parser.theme import extract_theme_colors

logger = logging.getLogger(__name__)


def get_design_spec(
    template_path: str,
    force_refresh: bool = False,
    is_defence: bool = False,
) -> DesignSpec:
    """
    Return DesignSpec for a template (cached in memory + .designspec.json on disk).

    Shape XML and image bytes are re-scanned each call; only color/font tokens are cached on disk.
    """
    abs_path = os.path.abspath(template_path)
    with open(abs_path, "rb") as fh:
        data = fh.read()
    file_hash = hashlib.md5(data).hexdigest()
    cache_key = f"{abs_path}:{file_hash}:colors-only-v1:defence={is_defence}"

    if not force_refresh:
        cached = memory_cache_get(cache_key)
        if cached is not None:
            return cached

    zf = zipfile.ZipFile(BytesIO(data))
    theme_colors = extract_theme_colors(zf)
    scan = scan_template(zf, theme_colors, is_defence=is_defence)
    zf.close()

    cache_file = abs_path + ".designspec.json"
    tokens = None
    source = "heuristic"

    if not force_refresh:
        tokens, source = load_disk_tokens(cache_file, file_hash)
        if tokens is not None:
            logger.info("reusing cached design tokens", extra={"cache_file": cache_file})

    if tokens is None:
        tokens = {**scan["tokens"], "is_defence": is_defence}
        source = "heuristic"
        logger.info("scanned design tokens", extra={"tokens": tokens})
        save_disk_tokens(cache_file, file_hash, tokens, source)
    elif "option_labels" not in tokens or "is_defence" not in tokens:
        tokens = {
            **tokens,
            "option_labels": scan["tokens"].get("option_labels"),
            "is_defence": is_defence,
        }
        save_disk_tokens(cache_file, file_hash, tokens, source)
    else:
        tokens["is_defence"] = is_defence

    spec = spec_from_tokens_and_scan(tokens, source, scan)
    memory_cache_set(cache_key, spec)
    return spec
