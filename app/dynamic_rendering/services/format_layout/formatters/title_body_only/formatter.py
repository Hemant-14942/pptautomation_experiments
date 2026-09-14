"""Clone body text into BODY_TEXTBOX with wrap, vertical center, and shrink-to-fit."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.shared.text_layout import configure_body_text_layout
from app.dynamic_rendering.utils.xml.shape_mutators import clone_and_place


def format_body_only(body_shape_el: etree._Element, dspec=None) -> etree._Element:
    from app.dynamic_rendering.services.format_layout.formatters.title_body_only.constants import (
        body_textbox_for,
    )
    box = body_textbox_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    configure_body_text_layout(clone)
    return clone
