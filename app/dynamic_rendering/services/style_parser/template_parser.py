"""
Parse template .pptx into SlideDesign list (one per template slide).
"""

from __future__ import annotations

import zipfile
from io import BytesIO
from typing import Any

from lxml import etree
from pptx import Presentation
from pptx.util import Emu

from app.dynamic_rendering.constants.xml_namespaces import A, P
from app.dynamic_rendering.domain.models.slide_design import ShapeStyle, SlideDesign
from app.dynamic_rendering.services.style_parser.theme import extract_theme


def _xml_bytes(elem: etree._Element | None) -> bytes | None:
    """Serialize p:bg (or any element) to bytes so we can clone it later."""
    if elem is None:
        return None
    return etree.tostring(elem)


def _bg_kind(bg_elem: etree._Element | None) -> str:
    """
    Classify slide background type.

    XML tree we READ:
      p:cSld
        p:bg
          a:blip          → "image"
          a:solidFill     → "solid"
    """
    if bg_elem is None:
        return "none"
    blip = bg_elem.find(".//{%s}blip" % A)
    if blip is not None:
        return "image"
    solid = bg_elem.find(".//{%s}solidFill" % A)
    if solid is not None:
        return "solid"
    return "other"


def _parse_hex(elem: etree._Element | None) -> str | None:
    """
    Read hex color from a:solidFill child.

    Returns "AABBCC" for srgbClr, or "scheme:accent1" for theme reference.
    """
    if elem is None:
        return None
    srgb = elem.find("{%s}srgbClr" % A)
    if srgb is not None:
        return srgb.get("val", "").upper()
    scheme = elem.find("{%s}schemeClr" % A)
    if scheme is not None:
        return f"scheme:{scheme.get('val', '')}"
    return None


def _shape_style(sp_elem: etree._Element, spPr: etree._Element | None) -> dict[str, Any]:
    """
    Extract a flat dict of style fields from one shape XML element.

    XML tree we READ (example p:sp):
      p:sp  name="..."
        p:spPr
          a:solidFill → fill_hex
        p:txBody
          a:r / a:rPr → font_name, font_size_pt, font_color_hex
    """
    info: dict[str, Any] = {
        "name": sp_elem.get("name", ""),
        "is_group": False,
        "is_table": False,
        "is_picture": False,
        "has_text": False,
        "sample_text": "",
        "fill_hex": None,
        "font_name": None,
        "font_size_pt": None,
        "font_color_hex": None,
    }

    tag = etree.QName(sp_elem).localname
    if tag == "grpSp":
        info["is_group"] = True
    elif tag == "graphicFrame":
        graphic = sp_elem.find(".//{%s}graphicData" % A)
        uri = graphic.get("uri", "") if graphic is not None else ""
        if "table" in uri.lower():
            info["is_table"] = True
    elif tag == "pic":
        info["is_picture"] = True

    if spPr is not None:
        solid = spPr.find("{%s}solidFill" % A)
        info["fill_hex"] = _parse_hex(solid)

    txBody = sp_elem.find("{%s}txBody" % P)
    if txBody is not None:
        info["has_text"] = True
        info["sample_text"] = "".join(t.text or "" for t in txBody.iter("{%s}t" % A)).strip()[:80]
        first_r = txBody.find(".//{%s}r" % A)
        if first_r is not None:
            rPr = first_r.find("{%s}rPr" % A)
            if rPr is not None:
                sz = rPr.get("sz")
                if sz:
                    try:
                        info["font_size_pt"] = int(int(sz) / 100)
                    except ValueError:
                        pass
                latin = rPr.find("{%s}latin" % A)
                if latin is not None:
                    info["font_name"] = latin.get("typeface")
                solid = rPr.find("{%s}solidFill" % A)
                info["font_color_hex"] = _parse_hex(solid)
            else:
                defRPr = txBody.find("{%s}lstStyle/{%s}defRPr" % (P, A))
                if defRPr is not None:
                    sz = defRPr.get("sz")
                    if sz:
                        try:
                            info["font_size_pt"] = int(int(sz) / 100)
                        except ValueError:
                            pass
                    latin = defRPr.find("{%s}latin" % A)
                    if latin is not None:
                        info["font_name"] = latin.get("typeface")

    return info


def _geom(spPr: etree._Element | None) -> tuple[int | None, int | None, int | None, int | None]:
    """
    Read shape position and size from p:spPr/a:xfrm.

    Returns (left, top, width, height) in EMU.
    """
    if spPr is None:
        return None, None, None, None
    off = spPr.find("{%s}xfrm/{%s}off" % (A, A))
    ext = spPr.find("{%s}xfrm/{%s}ext" % (A, A))
    if off is None or ext is None:
        return None, None, None, None
    return (
        int(off.get("x", 0)),
        int(off.get("y", 0)),
        int(ext.get("cx", 0)),
        int(ext.get("cy", 0)),
    )


def emu_to_in(emu: int | None) -> float | None:
    """Convert EMU to inches for debugging or logging."""
    return None if emu is None else Emu(emu).inches


def hex_no_hash(value: str | None) -> str | None:
    """Strip # prefix from hex; skip scheme: colors."""
    if value is None:
        return None
    if value.startswith("scheme:"):
        return None
    return value.lstrip("#").upper()


def parse_template(template_path: str) -> tuple[Presentation, list[SlideDesign], bytes]:
    """
    Read template file and return designs for slide matching + assembly.

    Returns:
      prs           = python-pptx Presentation (optional use later)
      designs       = list[SlideDesign] one per slide
      archive_bytes = raw file bytes (optional cache use later)
    """
    with open(template_path, "rb") as fh:
        archive_bytes = fh.read()

    zip_f = zipfile.ZipFile(BytesIO(archive_bytes))
    theme_font, theme_colors = extract_theme(zip_f)
    zip_f.close()

    prs = Presentation(template_path)
    designs: list[SlideDesign] = []

    for idx, slide in enumerate(prs.slides):
        sxml = slide._element
        cSld = sxml.find("{%s}cSld" % P)
        bg_elem = cSld.find("{%s}bg" % P) if cSld is not None else None

        shapes: list[ShapeStyle] = []
        for sp in sxml.iter():
            if etree.QName(sp).localname not in {"sp", "pic", "grpSp", "graphicFrame"}:
                continue
            spPr = sp.find("{%s}spPr" % P)
            left, top, w, h = _geom(spPr)
            info = _shape_style(sp, spPr)
            shapes.append(
                ShapeStyle(
                    name=info["name"],
                    shape_type=etree.QName(sp).localname,
                    left=left,
                    top=top,
                    width=w,
                    height=h,
                    has_text=info["has_text"],
                    sample_text=info["sample_text"],
                    fill_hex=info["fill_hex"],
                    font_name=info["font_name"],
                    font_size_pt=info["font_size_pt"],
                    font_color_hex=info["font_color_hex"],
                    is_group=info["is_group"],
                    is_table=info["is_table"],
                    is_picture=info["is_picture"],
                )
            )

        designs.append(
            SlideDesign(
                index=idx,
                layout_name=slide.slide_layout.name,
                background_xml=_xml_bytes(bg_elem),
                background_kind=_bg_kind(bg_elem),
                theme_font=theme_font,
                theme_colors=theme_colors,
                shapes=shapes,
            )
        )

    return prs, designs, archive_bytes
