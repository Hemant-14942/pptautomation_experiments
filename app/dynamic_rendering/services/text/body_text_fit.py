"""Estimate body font size so wrapped text fits inside the shape box."""

from __future__ import annotations

import math

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import (
    EMU_PER_PT,
    TITLE_HEADING_AVG_CHAR_WIDTH_EM,
)
from app.dynamic_rendering.constants.template_design import FIXED_BODY_FONT_PT
from app.dynamic_rendering.utils.xml.helpers import q, text_of

BODY_LINE_SPACING = 1.35
BODY_MIN_FONT_PT = 25.0
BODY_FIT_HEIGHT_FRACTION = 0.88
BODY_EFFECTIVE_WIDTH_FRACTION = 0.82
BODY_PARAGRAPH_GAP_LINES = 0.35


def _paragraphs(el: etree._Element) -> list[etree._Element]:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return []
    return [p for p in txBody.findall(q("a:p")) if text_of(p).strip()]


def estimate_wrapped_line_count(
    el: etree._Element,
    box_width_emu: int,
    font_size_pt: float,
) -> int:
    paragraphs = _paragraphs(el)
    if not paragraphs:
        return 0
    if box_width_emu <= 0:
        return len(paragraphs)

    effective_width = int(box_width_emu * BODY_EFFECTIVE_WIDTH_FRACTION)
    char_width_emu = TITLE_HEADING_AVG_CHAR_WIDTH_EM * font_size_pt * EMU_PER_PT
    if char_width_emu <= 0:
        return len(paragraphs)

    chars_per_line = max(1, int(effective_width / char_width_emu))
    text_lines = 0
    for paragraph in paragraphs:
        text = text_of(paragraph).strip()
        text_lines += max(1, math.ceil(len(text) / chars_per_line))
    gap_lines = max(0, len(paragraphs) - 1) * BODY_PARAGRAPH_GAP_LINES
    return int(math.ceil(text_lines + gap_lines))


def line_height_emu(font_size_pt: float) -> int:
    return int(font_size_pt * EMU_PER_PT * BODY_LINE_SPACING)


def fit_body_font_size_pt(
    el: etree._Element,
    box_width_emu: int,
    box_height_emu: int,
    baseline_font_size_pt: float = FIXED_BODY_FONT_PT,
) -> float:
    """Return a font size that should fit wrapped body text in the box height."""
    if box_height_emu <= 0 or box_width_emu <= 0:
        return baseline_font_size_pt

    usable_height = int(box_height_emu * BODY_FIT_HEIGHT_FRACTION)
    for font_pt in range(int(baseline_font_size_pt), int(BODY_MIN_FONT_PT) - 1, -1):
        lines = estimate_wrapped_line_count(el, box_width_emu, float(font_pt))
        if lines * line_height_emu(float(font_pt)) <= usable_height:
            return float(font_pt)
    return BODY_MIN_FONT_PT
