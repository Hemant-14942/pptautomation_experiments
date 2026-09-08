"""Read theme color roles from ppt/theme/theme1.xml (for schemeClr resolution only)."""

from __future__ import annotations

import zipfile

from lxml import etree

from app.dynamic_rendering.constants.xml_namespaces import A


def extract_theme_colors(zip_f: zipfile.ZipFile) -> dict[str, str]:
    """
    Get color_role → hex from the first theme file in the zip.

    Used when shape XML references a:schemeClr (e.g. accent1) instead of direct srgbClr.
    Font family is fixed separately (Cambria) — not read from theme.
    """
    theme_names = [
        n for n in zip_f.namelist()
        if n.startswith("ppt/theme/theme") and n.endswith(".xml")
    ]
    if not theme_names:
        return {}

    root = etree.fromstring(zip_f.read(theme_names[0]))
    scheme = root.find(".//{%s}clrScheme" % A)
    colors: dict[str, str] = {}

    if scheme is not None:
        for child in scheme:
            role = etree.QName(child).localname
            srgb = child.find("{%s}srgbClr" % A)
            if srgb is not None:
                colors[role] = srgb.get("val", "").upper()

    return colors
