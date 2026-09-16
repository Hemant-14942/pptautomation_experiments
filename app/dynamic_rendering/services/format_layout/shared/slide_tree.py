"""Helpers for swapping shapes on a slide's shape tree."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.utils.xml.helpers import local_name, parse_emu, q

_TOP_LEVEL_SHAPE_TAGS = {"sp", "pic", "grpSp", "graphicFrame", "cxnSp"}


def replace_shape(sp_tree: etree._Element, orig_el: etree._Element, clone_el: etree._Element) -> None:
    if orig_el.getparent() is not None:
        sp_tree.remove(orig_el)
    sp_tree.append(clone_el)


def _xfrm_for(elem: etree._Element) -> etree._Element | None:
    """Find the a:xfrm that carries this shape's position, wherever it lives.

    p:sp / p:pic / p:cxnSp keep it under p:spPr; p:grpSp under p:grpSpPr;
    p:graphicFrame (tables) keep a bare p:xfrm as a direct child.
    """
    tag = local_name(elem)
    if tag == "graphicFrame":
        return elem.find(q("p:xfrm"))
    container_tag = "p:grpSpPr" if tag == "grpSp" else "p:spPr"
    container = elem.find(q(container_tag))
    if container is None:
        return None
    return container.find(q("a:xfrm"))


def shift_shapes_down(sp_tree: etree._Element, shift_emu: int) -> None:
    """Nudge every top-level shape's y offset down by shift_emu, in place.

    For slides whose type we could not detect (no formatter runs, so nothing
    repositions them), this keeps them clear of a template's reserved top
    banner instead of letting the original input coordinates overlap it.
    A no-op when shift_emu <= 0 (e.g. templates with no reserved banner).
    """
    if shift_emu <= 0:
        return
    for child in sp_tree:
        if local_name(child) not in _TOP_LEVEL_SHAPE_TAGS:
            continue
        xfrm = _xfrm_for(child)
        if xfrm is None:
            continue
        off_el = xfrm.find(q("a:off"))
        if off_el is None:
            continue
        y = parse_emu(off_el.get("y"))
        off_el.set("y", str(y + shift_emu))
