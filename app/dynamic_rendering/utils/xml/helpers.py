"""
Small helpers to READ shape XML inside a .pptx slide.

No file I/O here — only lxml element operations.
"""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.constants.xml_namespaces import NS


def q(tag: str) -> str:
    """
    Turn 'p:sp' into the full tag name lxml needs.

    Input:  "p:spPr"
    Output: "{http://.../presentationml/2006/main}spPr"
    """
    prefix, local = tag.split(":")          # split "p" and "spPr"
    return "{%s}%s" % (NS[prefix], local)   # glue namespace URL + local name


def local_name(elem: etree._Element) -> str:
    """
    Get short tag name without namespace.

    Input:  element for {http://...}sp
    Output: "sp"
    """
    return etree.QName(elem).localname


def prst_geom(sp: etree._Element) -> str | None:
    """
    Read preset shape type: roundRect, ellipse, rect, etc.

    XML:
      p:sp
        p:spPr
          a:prstGeom prst="roundRect"

    Returns None if shape has no prstGeom (freeform shape).
    """
    spPr = sp.find(q("p:spPr"))              # shape properties block
    if spPr is None:
        return None
    geom = spPr.find(q("a:prstGeom"))       # preset geometry tag
    return geom.get("prst") if geom is not None else None


def parse_emu(value: str | int | float | None, default: int = 0) -> int:
    """Parse an EMU attribute value; some decks store floats like '5729298.0'."""
    if value is None:
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def off_ext(
    elem: etree._Element,
    pref: str,
) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    """
    Read position (off) and size (ext) from a shape or group.

    pref is usually "p:spPr" for a shape or "p:grpSpPr" for a group.

    XML:
      p:sp
        p:spPr
          a:xfrm
            a:off  x="..." y="..."     ← top-left corner (EMU)
            a:ext  cx="..." cy="..."   ← width and height (EMU)

    Returns: ((x, y), (width, height)) or (None, None) if missing.
    """
    container = elem.find(q(pref))          # spPr or grpSpPr
    if container is None:
        return None, None

    xfrm = container.find(q("a:xfrm"))     # transform = position + size
    if xfrm is None:
        return None, None

    off = xfrm.find(q("a:off"))           # offset = where shape starts
    ext = xfrm.find(q("a:ext"))           # extent = how big shape is

    off_t = (parse_emu(off.get("x")), parse_emu(off.get("y"))) if off is not None else None
    ext_t = (parse_emu(ext.get("cx")), parse_emu(ext.get("cy"))) if ext is not None else None
    return off_t, ext_t


def text_of(elem: etree._Element) -> str:
    """
    Collect all visible text inside a shape (all a:t runs).

    XML:
      p:txBody
        a:p
          a:r
            a:t  "Question"
    """
    return "".join(t.text or "" for t in elem.iter(q("a:t"))).strip()


def in_range(
    ext: tuple[int, int] | None,
    cx_range: tuple[int, int],
    cy_range: tuple[int, int],
) -> bool:
    """
    Check if shape width/height falls inside allowed min/max ranges.

    Used to detect question pill vs option pill by size buckets in shape_geometry.py.
    """
    if not ext:
        return False
    cx, cy = ext
    return cx_range[0] <= cx <= cx_range[1] and cy_range[0] <= cy <= cy_range[1]


def representative_rpr(elem: etree._Element) -> etree._Element | None:
    """
    Find the run properties (rPr) that best describe text styling.

    Tries: first a:r/a:rPr → lstStyle/defRPr → endParaRPr.
    Works for p:txBody (shapes) and a:txBody (table cells).
    """
    txBody = elem.find(q("p:txBody"))
    if txBody is None:
        txBody = elem.find(q("a:txBody"))
    if txBody is None:
        return None

    r = txBody.find(".//" + q("a:r"))
    rPr = r.find(q("a:rPr")) if r is not None else None
    if rPr is None:
        rPr = txBody.find(q("a:lstStyle") + "/" + q("a:defRPr"))
    if rPr is None:
        rPr = txBody.find(".//" + q("a:endParaRPr"))
    return rPr


def font_size_pt(elem: etree._Element) -> float | None:
    """
    Read font size in points from a shape's text.

    XML stores sz in 1/100 pt — e.g. 80pt → sz="8000".
    """
    rPr = representative_rpr(elem)
    sz = rPr.get("sz") if rPr is not None else None
    if not sz:
        return None
    try:
        return int(sz) / 100.0
    except ValueError:
        return None