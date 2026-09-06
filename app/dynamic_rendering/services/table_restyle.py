"""Restyling for `<a:tbl>` tables carried over from the input deck."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.constants.xml_namespaces import FILL_TAGS
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import set_all_run_colors


def set_tc_fill(tcPr: etree._Element, hex_val: str) -> None:
    for child in list(tcPr):
        if etree.QName(child).localname in FILL_TAGS:
            tcPr.remove(child)
    solid = etree.SubElement(tcPr, q("a:solidFill"))
    srgb = etree.SubElement(solid, q("a:srgbClr"))
    srgb.set("val", hex_val)


def restyle_table(graphic_frame: etree._Element, dspec: DesignSpec) -> None:
    """Restyle only the header row using MCQ heading tokens (heading_fill / heading_text_color)."""
    tbl = graphic_frame.find(".//" + q("a:tbl"))
    if tbl is None:
        return
    trs = tbl.findall(q("a:tr"))
    if not trs:
        return
    header_tr = trs[0]
    for tc in header_tr.findall(q("a:tc")):
        if tc.get("hMerge") == "1" or tc.get("vMerge") == "1":
            continue
        tcPr = tc.find(q("a:tcPr"))
        if tcPr is None:
            tcPr = etree.SubElement(tc, q("a:tcPr"))
        set_tc_fill(tcPr, dspec.heading_fill)
        set_all_run_colors(tc, dspec.heading_text_color)
