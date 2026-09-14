"""Clone body text into the fixed full-slide box with wrap, vertical center, normAutofit."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.body_only.constants import body_textbox_for
from app.dynamic_rendering.services.format_layout.shared.text_layout import set_vertical_center_anchor
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
)


def format_body_text(body_shape_el: etree._Element, dspec=None) -> etree._Element:
    box = body_textbox_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    enable_text_wrapping(clone)
    set_vertical_center_anchor(clone)
    enable_shrink_to_fit(clone)
    return clone
