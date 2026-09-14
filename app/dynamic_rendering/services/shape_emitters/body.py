"""Emit body text shapes with template body styling."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.template_design import FIXED_BODY_FONT_PT
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    BODY_LONG_LIST_PARAGRAPH_THRESHOLD,
)
from app.dynamic_rendering.services.format_layout.shared.text_layout import count_nonempty_paragraphs
from app.dynamic_rendering.services.text.body_text_fit import fit_body_font_size_pt
from app.dynamic_rendering.utils.xml.helpers import off_ext, q
from app.dynamic_rendering.utils.xml.shape_mutators import (
    enable_shrink_to_fit,
    set_all_run_colors,
    set_all_run_fonts,
    set_all_run_sizes,
    strip_run_overrides,
)


def emit_body(spTree: etree._Element, item: dict[str, Any], dspec: DesignSpec) -> None:
    xml_el = copy.deepcopy(item["xml"])
    txBody = xml_el.find(q("p:txBody"))
    if txBody is not None:
        strip_run_overrides(txBody)
        set_all_run_colors(xml_el, dspec.body_text_color)
        if dspec.body_font:
            set_all_run_fonts(xml_el, dspec.body_font)
        _, ext = off_ext(xml_el, "p:spPr")
        box_width = ext[0] if ext else 0
        box_height = ext[1] if ext else 0
        if count_nonempty_paragraphs(xml_el) > BODY_LONG_LIST_PARAGRAPH_THRESHOLD:
            font_pt = fit_body_font_size_pt(xml_el, box_width, box_height, FIXED_BODY_FONT_PT)
        else:
            font_pt = FIXED_BODY_FONT_PT
        set_all_run_sizes(xml_el, font_pt)
        enable_shrink_to_fit(xml_el)
    spTree.append(xml_el)
