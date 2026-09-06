"""Public entry: get_design_spec(template_path)."""

from __future__ import annotations

import hashlib
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
from app.dynamic_rendering.services.style_parser.theme import extract_theme


def get_design_spec(template_path: str, force_refresh: bool = False) -> DesignSpec:
    """
    Return DesignSpec for a template (cached in memory + .designspec.json on disk).

    Shape XML and image bytes are re-scanned each call; only color/font tokens are cached on disk.
    """
    abs_path = os.path.abspath(template_path)
    with open(abs_path, "rb") as fh:
        data = fh.read()
    file_hash = hashlib.md5(data).hexdigest()
    cache_key = f"{abs_path}:{file_hash}"

    if not force_refresh:
        cached = memory_cache_get(cache_key)
        if cached is not None:
            return cached

    zf = zipfile.ZipFile(BytesIO(data))
    theme_font, theme_colors = extract_theme(zf)
    scan = scan_template(zf, theme_colors, theme_font)
    zf.close()

    cache_file = abs_path + ".designspec.json"
    tokens = None
    source = "heuristic"

    if not force_refresh:
        tokens, source = load_disk_tokens(cache_file, file_hash)
        if tokens is not None:
            print(f"[design-spec] reusing cached design tokens ({cache_file})")

    if tokens is None:
        tokens = scan["tokens"]
        source = "heuristic"
        print(f"[design-spec] scan tokens (no AI): {tokens}")
        save_disk_tokens(cache_file, file_hash, tokens, source)

    spec = spec_from_tokens_and_scan(tokens, source, scan)
    memory_cache_set(cache_key, spec)
    return spec
