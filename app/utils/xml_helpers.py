"""Generic, stateless read-only accessors over raw DrawingML/PresentationML
XML elements (lxml). Shared by app/core/design_spec.py and
app/core/template_converter/* -- both walk the same `<p:sp>`/`<p:pic>`/
`<p:grpSp>` shape trees and previously each carried their own copy of these.
"""
from __future__ import annotations

from lxml import etree

from app.constants.xml_namespaces import NS


def q(tag: str) -> str:
    """'p:sp' -> '{http://.../presentationml/2006/main}sp'"""
    prefix, local = tag.split(":")
    return "{%s}%s" % (NS[prefix], local)


def local_name(elem: etree._Element) -> str:
    return etree.QName(elem).localname


def prst_geom(sp: etree._Element) -> str | None:
    """The shape's preset geometry name (e.g. 'roundRect', 'ellipse'), or
    None if it has no <a:prstGeom> (e.g. a freeform/custGeom shape)."""
    spPr = sp.find(q("p:spPr"))
    if spPr is None:
        return None
    geom = spPr.find(q("a:prstGeom"))
    return geom.get("prst") if geom is not None else None


def off_ext(elem: etree._Element, pref: str) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    """(offset, extent) in EMU from `<{pref}><a:xfrm><a:off/a:ext>`, e.g.
    pref="p:spPr" for a shape or "p:grpSpPr" for a group."""
    container = elem.find(q(pref))
    if container is None:
        return None, None
    xfrm = container.find(q("a:xfrm"))
    if xfrm is None:
        return None, None
    off = xfrm.find(q("a:off"))
    ext = xfrm.find(q("a:ext"))
    off_t = (int(off.get("x", 0)), int(off.get("y", 0))) if off is not None else None
    ext_t = (int(ext.get("cx", 0)), int(ext.get("cy", 0))) if ext is not None else None
    return off_t, ext_t


def text_of(elem: etree._Element) -> str:
    """Concatenated text of every <a:t> run under `elem`."""
    return "".join(t.text or "" for t in elem.iter(q("a:t"))).strip()


def in_range(ext: tuple[int, int] | None, cx_range: tuple[int, int], cy_range: tuple[int, int]) -> bool:
    if not ext:
        return False
    cx, cy = ext
    return cx_range[0] <= cx <= cx_range[1] and cy_range[0] <= cy <= cy_range[1]


def representative_rpr(elem: etree._Element) -> etree._Element | None:
    """The rPr that best represents a shape's/cell's text styling: the
    first a:r/a:rPr, else a:lstStyle/a:defRPr, else the first
    a:endParaRPr. Handles both <p:txBody> (shapes) and <a:txBody> (table
    cells)."""
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
    """Baseline font size (pt) from a shape's representative run (see
    representative_rpr), or None if nothing is set."""
    rPr = representative_rpr(elem)
    sz = rPr.get("sz") if rPr is not None else None
    if not sz:
        return None
    try:
        return int(sz) / 100.0
    except ValueError:
        return None
