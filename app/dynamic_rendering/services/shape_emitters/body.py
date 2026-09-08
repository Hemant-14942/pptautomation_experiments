"""Emit body text shapes with template body styling."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.template_design import FIXED_BODY_FONT_PT
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import (
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
        set_all_run_sizes(xml_el, FIXED_BODY_FONT_PT)
    spTree.append(xml_el)
