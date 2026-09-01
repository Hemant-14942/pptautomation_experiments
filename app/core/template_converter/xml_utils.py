"""Low-level shape-XML *mutation* helpers used while emitting the output
deck: cloning a template shape into a new position, overwriting its fill/
text/run-colors/fonts, renumbering ids, stripping run-level overrides so the
template's theme cascades, etc.

Read-only accessors (q, local_name, prst_geom, off_ext, text_of) live in
app/utils/xml_helpers.py -- this module is specifically the "write" side.
"""
from __future__ import annotations

import copy

from lxml import etree

from app.constants.shape_geometry import RECTS_CLOSE_TOLERANCE
from app.constants.xml_namespaces import FILL_TAGS
from app.utils.xml_helpers import q


def strip_run_overrides(txBody: etree._Element) -> None:
    """Remove per-run font / fill overrides so the template theme cascades.

    Deliberately leaves size / bold / italic / underline attributes alone
    -- those belong to the input's own formatting/emphasis, not to the
    template's visual language, and stripping them would collapse e.g.
    the big question numbering and the small footnote text to the same
    default size.
    """
    for rPr in txBody.iter(q("a:rPr")):
        for child in list(rPr):
            local = etree.QName(child).localname
            if local in {
                "latin", "ea", "cs", "sym",
                "solidFill", "gradFill", "noFill", "highlight",
                "uLnTx", "uLn", "uFillTx", "uFill",
                "effectLst", "effectDag", "extLst",
            }:
                rPr.remove(child)
    for end in txBody.iter(q("a:endParaRPr")):
        for child in list(end):
            local = etree.QName(child).localname
            if local in {"latin", "ea", "cs", "sym", "solidFill", "gradFill", "noFill"}:
                end.remove(child)


def set_shape_fill(sp_el: etree._Element, hex_val: str) -> None:
    spPr = sp_el.find(q("p:spPr"))
    if spPr is None:
        return
    for child in list(spPr):
        if etree.QName(child).localname in FILL_TAGS:
            spPr.remove(child)
    insert_at = 0
    for i, child in enumerate(spPr):
        if etree.QName(child).localname in {"xfrm", "custGeom", "prstGeom"}:
            insert_at = i + 1
    solid = etree.Element(q("a:solidFill"))
    srgb = etree.SubElement(solid, q("a:srgbClr"))
    srgb.set("val", hex_val)
    spPr.insert(insert_at, solid)


def set_text(el: etree._Element, text: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    t_el = txBody.find(".//" + q("a:t"))
    if t_el is not None:
        t_el.text = text


def set_all_run_colors(el: etree._Element, hex_val: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    targets = list(txBody.iter(q("a:rPr"))) + list(txBody.iter(q("a:endParaRPr")))
    for rPr in targets:
        for child in list(rPr):
            if etree.QName(child).localname in {"noFill", "solidFill", "gradFill"}:
                rPr.remove(child)
        solid = etree.Element(q("a:solidFill"))
        srgb = etree.SubElement(solid, q("a:srgbClr"))
        srgb.set("val", hex_val)
        rPr.insert(0, solid)


def set_all_run_fonts(el: etree._Element, font_name: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    for rPr in list(txBody.iter(q("a:rPr"))) + list(txBody.iter(q("a:endParaRPr"))):
        for tag in ("latin", "ea", "cs", "sym"):
            existing = rPr.find(q(f"a:{tag}"))
            if existing is None:
                existing = etree.SubElement(rPr, q(f"a:{tag}"))
            existing.set("typeface", font_name)


def set_all_run_sizes(el: etree._Element, size_pt: float) -> None:
    """Set every run's (and endParaRPr's) `sz` attribute (hundredths of a
    point) in a shape's txBody -- mirrors set_all_run_colors/
    set_all_run_fonts. Only meant to be called when a caller has actually
    computed a different size to apply; leave the template's own baked-in
    size untouched otherwise."""
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    sz_str = str(int(round(size_pt * 100)))
    for rPr in list(txBody.iter(q("a:rPr"))) + list(txBody.iter(q("a:endParaRPr"))):
        rPr.set("sz", sz_str)


def enable_text_wrapping(el: etree._Element) -> None:
    """Enable text wrapping (wrap="square") and set top-left alignment for
    a text shape's bodyPr, so long headings can wrap vertically instead of
    overflowing or shrinking. Also sets vertical anchor to top."""
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    bodyPr = txBody.find(q("a:bodyPr"))
    if bodyPr is None:
        return
    bodyPr.set("wrap", "square")
    bodyPr.set("anchorCtr", "0")
    bodyPr.set("anchor", "t")
    # Set left-to-right text direction
    bodyPr.set("rtlCol", "0")
    # Set paragraph alignment to left
    for p in txBody.findall(q("a:p")):
        pPr = p.find(q("a:pPr"))
        if pPr is None:
            pPr = etree.Element(q("a:pPr"))
            p.insert(0, pPr)
        pPr.set("algn", "l")


def clone_and_place(el: etree._Element, off: tuple[int, int] | None, ext: tuple[int, int] | None) -> etree._Element:
    clone = copy.deepcopy(el)
    spPr = clone.find(q("p:spPr"))
    if spPr is not None and off and ext:
        xfrm = spPr.find(q("a:xfrm"))
        if xfrm is None:
            xfrm = etree.SubElement(spPr, q("a:xfrm"))
        off_el = xfrm.find(q("a:off"))
        if off_el is None:
            off_el = etree.SubElement(xfrm, q("a:off"))
        off_el.set("x", str(off[0]))
        off_el.set("y", str(off[1]))
        ext_el = xfrm.find(q("a:ext"))
        if ext_el is None:
            ext_el = etree.SubElement(xfrm, q("a:ext"))
        ext_el.set("cx", str(ext[0]))
        ext_el.set("cy", str(ext[1]))
    return clone


def place_group(grp_el: etree._Element, off: tuple[int, int] | None, ext: tuple[int, int] | None) -> None:
    """Translate a whole grpSp to a new absolute position/size, leaving the
    child-coordinate-space (chOff/chExt) and every child's own offsets
    untouched -- this is a pure rigid-body translation."""
    grpSpPr = grp_el.find(q("p:grpSpPr"))
    if grpSpPr is None:
        return
    xfrm = grpSpPr.find(q("a:xfrm"))
    if xfrm is None:
        return
    off_el = xfrm.find(q("a:off"))
    ext_el = xfrm.find(q("a:ext"))
    if off_el is not None and off:
        off_el.set("x", str(off[0]))
        off_el.set("y", str(off[1]))
    if ext_el is not None and ext:
        ext_el.set("cx", str(ext[0]))
        ext_el.set("cy", str(ext[1]))


def strip_blip_ext_lst(blip: etree._Element | None) -> None:
    """Drop <a:extLst> children of a <a:blip> -- e.g. the "artistic
    effects" a14:imgLayer extension -- which can carry their OWN
    r:embed reference to a second image, separate from the blip's main
    embed. We only ever rewire the main embed when re-homing a cloned
    picture into the output, so leaving this in place would dangle."""
    if blip is None:
        return
    for ext_lst in list(blip.findall(q("a:extLst"))):
        blip.remove(ext_lst)


def renumber_ids(el: etree._Element, id_state: dict[str, int]) -> None:
    for cNvPr in el.iter(q("p:cNvPr")):
        id_state["next"] += 1
        cNvPr.set("id", str(id_state["next"]))


def rects_close(off1, ext1, off2, ext2, tol: int = RECTS_CLOSE_TOLERANCE) -> bool:
    if not (off1 and ext1 and off2 and ext2):
        return False
    return abs(off1[0] - off2[0]) < tol and abs(off1[1] - off2[1]) < tol
