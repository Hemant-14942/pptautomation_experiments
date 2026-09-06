"""Write in-memory zip parts to a .pptx file on disk."""

from __future__ import annotations

import zipfile
from pathlib import Path


def write_archive(out_parts: dict[str, bytes], output_path: str) -> None:
    """Write all zip parts to output_path as a deflated .pptx archive."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, blob in out_parts.items():
            zf.writestr(name, blob)
