"""Clone body text into BODY_TEXTBOX with wrap, vertical center, and shrink-to-fit."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.title_body_only.constants import BODY_TEXTBOX
from app.dynamic_rendering.services.format_layout.shared.text_layout import set_vertical_center_anchor
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
)


def format_body_only(body_shape_el: etree._Element) -> etree._Element:
    off = (BODY_TEXTBOX["x"], BODY_TEXTBOX["y"])
    ext = (BODY_TEXTBOX["width"], BODY_TEXTBOX["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    enable_text_wrapping(clone)
    set_vertical_center_anchor(clone)
    enable_shrink_to_fit(clone)
    return clone
