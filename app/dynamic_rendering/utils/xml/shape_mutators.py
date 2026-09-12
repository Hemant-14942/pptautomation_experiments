"""
Change shape XML: colors, fonts, text, clone, move, new ids.

Used when emitters build output slides from template shapes.
"""

from __future__ import annotations

import copy

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import RECTS_CLOSE_TOLERANCE
from app.dynamic_rendering.constants.xml_namespaces import FILL_TAGS
from app.dynamic_rendering.utils.xml.helpers import q


def strip_run_overrides(txBody: etree._Element) -> None:
    """
    Remove old font/color from text so template style can apply.

    XML tree we EDIT:
      p:txBody  (or a:txBody in table cells)
        a:p
          a:r
            a:rPr          ← we clean children here (font, solidFill, etc.)
          a:endParaRPr     ← we clean here too
    We KEEP sz, bold, italic on rPr — those are content size (e.g. 80pt title).
    """
    # walk every text run properties node in this text body
    for rPr in txBody.iter(q("a:rPr")):
        # copy children to list so we can remove while looping
        for child in list(rPr):
            # get short tag name like "latin" or "solidFill"
            local = etree.QName(child).localname
            # if this child is font or fill override, delete it
            if local in {
                "latin", "ea", "cs", "sym",
                "solidFill", "gradFill", "noFill", "highlight",
                "uLnTx", "uLn", "uFillTx", "uFill",
                "effectLst", "effectDag", "extLst",
            }:
                rPr.remove(child)

    # also clean end-of-paragraph run properties
    for end in txBody.iter(q("a:endParaRPr")):
        for child in list(end):
            local = etree.QName(child).localname
            if local in {"latin", "ea", "cs", "sym", "solidFill", "gradFill", "noFill"}:
                end.remove(child)


def set_shape_fill(sp_el: etree._Element, hex_val: str) -> None:
    """
    Set solid background color on a shape (pill, banner, etc.).

    XML tree we EDIT:
      p:sp
        p:spPr                    ← find this
          a:xfrm                  ← keep
          a:prstGeom              ← keep
          (old a:solidFill etc.)  ← DELETE all FILL_TAGS
          a:solidFill             ← INSERT new
            a:srgbClr val="015500"
    """
    # find shape properties under p:sp
    spPr = sp_el.find(q("p:spPr"))
    # no spPr means we cannot set fill
    if spPr is None:
        return

    # remove every existing fill type (solid, gradient, picture, etc.)
    for child in list(spPr):
        if etree.QName(child).localname in FILL_TAGS:
            spPr.remove(child)

    # default insert position is start of spPr
    insert_at = 0
    # put new fill AFTER xfrm/geometry tags (PowerPoint order matters)
    for i, child in enumerate(spPr):
        if etree.QName(child).localname in {"xfrm", "custGeom", "prstGeom"}:
            insert_at = i + 1

    # create new solid fill element
    solid = etree.Element(q("a:solidFill"))
    # create RGB color inside solid fill
    srgb = etree.SubElement(solid, q("a:srgbClr"))
    # set hex value without # (design team format)
    srgb.set("val", hex_val)
    # insert fill at computed position inside spPr
    spPr.insert(insert_at, solid)


def set_text(el: etree._Element, text: str) -> None:
    """
    Replace visible text in the first text run.

    XML tree we EDIT:
      p:sp
        p:txBody
          a:p
            a:r
              a:t   ← we set .text here
    """
    # try shape text body first
    txBody = el.find(q("p:txBody"))
    # table cells use a:txBody instead
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    # no text body means nothing to change
    if txBody is None:
        return
    # find first a:t text node anywhere under txBody
    t_el = txBody.find(".//" + q("a:t"))
    # replace its text content
    if t_el is not None:
        t_el.text = text


def set_all_run_colors(el: etree._Element, hex_val: str) -> None:
    """
    Set text color on every run in the shape.

    XML tree we EDIT:
      p:txBody / a:txBody
        a:r / a:endParaRPr
          a:rPr
            a:solidFill        ← remove old, add new
              a:srgbClr
    """
    # find shape text body
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return

    # collect all run property nodes to update
    targets = list(txBody.iter(q("a:rPr"))) + list(txBody.iter(q("a:endParaRPr")))
    # update each run's color
    for rPr in targets:
        # remove old fill tags on this run
        for child in list(rPr):
            if etree.QName(child).localname in {"noFill", "solidFill", "gradFill"}:
                rPr.remove(child)
        # build new solid fill for text color
        solid = etree.Element(q("a:solidFill"))
        srgb = etree.SubElement(solid, q("a:srgbClr"))
        srgb.set("val", hex_val)
        # insert fill at front of rPr
        rPr.insert(0, solid)


def set_all_run_fonts(el: etree._Element, font_name: str) -> None:
    """
    Set font on every text run (design team: Cambria).

    XML tree we EDIT:
      a:rPr
        a:latin typeface="Cambria"   ← set or create
    """
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return

    for rPr in list(txBody.iter(q("a:rPr"))) + list(txBody.iter(q("a:endParaRPr"))):
        # set latin/ea/cs/sym font slots (PowerPoint uses latin for English)
        for tag in ("latin", "ea", "cs", "sym"):
            existing = rPr.find(q(f"a:{tag}"))
            if existing is None:
                existing = etree.SubElement(rPr, q(f"a:{tag}"))
            existing.set("typeface", font_name)


def set_all_run_sizes(el: etree._Element, size_pt: float) -> None:
    """
    Set font size on all runs (when title auto-fit shrinks below 80pt).

    XML: a:rPr sz="8000" means 80pt (sz is 1/100 point).
    """
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return

    # convert points to PowerPoint sz string
    sz_str = str(int(round(size_pt * 100)))
    for rPr in list(txBody.iter(q("a:rPr"))) + list(txBody.iter(q("a:endParaRPr"))):
        rPr.set("sz", sz_str)


def enable_text_wrapping(el: etree._Element) -> None:
    """
    Allow long title to wrap inside banner.

    XML tree we EDIT:
      p:txBody
        a:bodyPr wrap="square" anchor="t"   ← enable wrap, top align
        a:p
          a:pPr algn="l"                      ← left align paragraph
    """
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
    bodyPr.set("rtlCol", "0")

    for p in txBody.findall(q("a:p")):
        pPr = p.find(q("a:pPr"))
        if pPr is None:
            pPr = etree.Element(q("a:pPr"))
            p.insert(0, pPr)
        pPr.set("algn", "l")


def set_text_center_align(el: etree._Element) -> None:
    """Center text horizontally and vertically inside a shape text box (e.g. MCQ option A/B/C/D)."""
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return

    bodyPr = txBody.find(q("a:bodyPr"))
    if bodyPr is None:
        bodyPr = etree.SubElement(txBody, q("a:bodyPr"))

    bodyPr.set("anchor", "ctr")
    bodyPr.set("anchorCtr", "0")

    for p in txBody.findall(q("a:p")):
        pPr = p.find(q("a:pPr"))
        if pPr is None:
            pPr = etree.Element(q("a:pPr"))
            p.insert(0, pPr)
        pPr.set("algn", "ctr")


def enable_shrink_to_fit(el: etree._Element) -> None:
    """PowerPoint shrink-text-on-overflow (a:normAutofit on bodyPr)."""
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    bodyPr = txBody.find(q("a:bodyPr"))
    if bodyPr is None:
        return
    for old_tag in ("normAutofit", "spAutoFit", "noAutofit"):
        old_child = bodyPr.find(q(f"a:{old_tag}"))
        if old_child is not None:
            bodyPr.remove(old_child)
    etree.SubElement(bodyPr, q("a:normAutofit"))


def clone_and_place(
    el: etree._Element,
    off: tuple[int, int] | None,
    ext: tuple[int, int] | None,
) -> etree._Element:
    """
    Copy template shape XML and move it to new position/size.

    XML tree we READ then WRITE on the clone:
      p:sp
        p:spPr
          a:xfrm
            a:off  x,y    ← we SET these from `off`
            a:ext  cx,cy  ← we SET these from `ext`
    """
    # deep copy so template DesignSpec XML is never mutated
    clone = copy.deepcopy(el)

    # find spPr on the clone (works for p:sp and p:pic with spPr)
    spPr = clone.find(q("p:spPr"))
    # only update if we have position, size, and spPr exists
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


def place_group(
    grp_el: etree._Element,
    off: tuple[int, int] | None,
    ext: tuple[int, int] | None,
) -> None:
    """
    Move a group shape (grpSp) — option pills often come as groups.

    XML tree we EDIT:
      p:grpSp
        p:grpSpPr
          a:xfrm
            a:off / a:ext   ← only change group box, not children inside
    """
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
    """
    Clean picture blip before rewiring image relationship.

    XML tree we EDIT:
      p:pic
        p:blipFill
          a:blip r:embed="rId5"
            a:extLst   ← REMOVE (extra broken image refs)
    """
    if blip is None:
        return
    for ext_lst in list(blip.findall(q("a:extLst"))):
        blip.remove(ext_lst)


def renumber_ids(el: etree._Element, id_state: dict[str, int]) -> None:
    """
    Assign unique shape ids on one slide (avoid duplicate id crashes).

    XML tree we EDIT:
      p:sp
        p:nvSpPr
          p:cNvPr id="9001"   ← bump this
    id_state starts at FIRST_SHAPE_ID_PER_SLIDE (9000).
    """
    for cNvPr in el.iter(q("p:cNvPr")):
        id_state["next"] += 1
        cNvPr.set("id", str(id_state["next"]))


def rects_close(off1, ext1, off2, ext2, tol: int = RECTS_CLOSE_TOLERANCE) -> bool:
    """
    Check if two shapes start at almost the same place.

    We only compare top-left corners (off), not full size.
    """
    if not (off1 and ext1 and off2 and ext2):
        return False
    x_close = abs(off1[0] - off2[0]) < tol
    y_close = abs(off1[1] - off2[1]) < tol
    return x_close and y_close