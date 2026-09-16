"""Restyling for `<a:tbl>` tables carried over from the input deck."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.constants.xml_namespaces import FILL_TAGS
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import set_all_run_colors



# Alternating body-row band colors: the one pattern every source we checked
# already agrees on (this template's own tableStyles.xml, the defence
# template's own hand-built sample table, and the input deck's own table
# style) — just not always reachable, since it depends on a style-ID lookup
# that silently fails when the destination template doesn't define that ID.
# Applied only as a fallback: never overrides a cell that already carries its
# own explicit fill from the input.
BODY_ROW_BAND_COLORS = ("E7E9EC", "CAD1D8")
BODY_ROW_TEXT_COLOR = "000000"


def set_tc_fill(tcPr: etree._Element, hex_val: str) -> None:
    for child in list(tcPr):
        if etree.QName(child).localname in FILL_TAGS:
            tcPr.remove(child)
    solid = etree.SubElement(tcPr, q("a:solidFill"))
    srgb = etree.SubElement(solid, q("a:srgbClr"))
    srgb.set("val", hex_val)


def _has_explicit_fill(tc: etree._Element) -> bool:
    tcPr = tc.find(q("a:tcPr"))
    if tcPr is None:
        return False
    return any(etree.QName(child).localname in FILL_TAGS for child in tcPr)


def _restyle_body_rows(trs: list[etree._Element]) -> None:
    """Fill only cells with no explicit fill of their own, alternating bands
    per data row so untouched (already-colored) cells are never disturbed."""
    for row_idx, tr in enumerate(trs):
        band_color = BODY_ROW_BAND_COLORS[row_idx % 2]
        for tc in tr.findall(q("a:tc")):
            if tc.get("hMerge") == "1" or tc.get("vMerge") == "1":
                continue
            if _has_explicit_fill(tc):
                continue
            tcPr = tc.find(q("a:tcPr"))
            if tcPr is None:
                tcPr = etree.SubElement(tc, q("a:tcPr"))
            set_tc_fill(tcPr, band_color)
            set_all_run_colors(tc, BODY_ROW_TEXT_COLOR)


def restyle_table(graphic_frame: etree._Element, dspec: DesignSpec) -> None:
    """Restyle the header row using MCQ question pill tokens, and fall back to
    a standard grey band pattern for any body cell that has no color of its
    own (see BODY_ROW_BAND_COLORS above)."""
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
        set_tc_fill(tcPr, dspec.question_pill_fill)
        set_all_run_colors(tc, dspec.question_pill_text_color)

    _restyle_body_rows(trs[1:])
