"""
Read theme colors and fonts from ppt/theme/theme1.xml inside a .pptx zip.
"""

from __future__ import annotations

import zipfile

from lxml import etree

from app.dynamic_rendering.constants.xml_namespaces import A


def extract_theme(zip_f: zipfile.ZipFile) -> tuple[str | None, dict[str, str]]:
    """
    Get (major_font_name, color_role → hex) from first theme file in zip.

    Returns:
      font   = e.g. "Cambria" or None
      colors = e.g. {"accent1": "015500", "dk1": "000000", ...}
    """
    # list all theme xml paths inside the zip
    theme_names = [
        n for n in zip_f.namelist()
        if n.startswith("ppt/theme/theme") and n.endswith(".xml")
    ]
    # no theme file → return empty defaults
    if not theme_names:
        return None, {}

    # read first theme xml as bytes
    xml = zip_f.read(theme_names[0])
    # parse bytes into lxml tree
    root = etree.fromstring(xml)

    # find color scheme block in theme
    scheme = root.find(".//{%s}clrScheme" % A)
    colors: dict[str, str] = {}

    if scheme is not None:
        # each child is a role: accent1, dk1, lt1, hlink, etc.
        for child in scheme:
            # role name without namespace, e.g. "accent1"
            role = etree.QName(child).localname
            # try direct RGB color
            srgb = child.find("{%s}srgbClr" % A)
            if srgb is not None:
                colors[role] = srgb.get("val", "").upper()
            else:
                # some themes use system color with lastClr fallback
                sys_clr = child.find("{%s}sysClr" % A)
                if sys_clr is not None:
                    colors[role] = "sys:" + (sys_clr.get("lastClr") or sys_clr.get("val") or "")

    # read major font (headings) from theme
    major = root.find(".//{%s}majorFont/{%s}latin" % (A, A))
    # read minor font (body) as backup
    minor = root.find(".//{%s}minorFont/{%s}latin" % (A, A))

    font = None
    # prefer major theme font if present
    if major is not None and major.get("typeface"):
        font = major.get("typeface")
    # else use minor font
    elif minor is not None and minor.get("typeface"):
        font = minor.get("typeface")

    return font, colors