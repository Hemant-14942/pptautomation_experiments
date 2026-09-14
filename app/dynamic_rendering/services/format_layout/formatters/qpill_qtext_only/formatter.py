"""Clone and place question pill + text shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_only.constants import (
    question_text_for,
)
from app.dynamic_rendering.services.format_layout.shared.qpill_formatters import (
    format_question_label,
    format_question_pill,
)
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
)


def format_question_text(text_el: etree._Element, dspec=None) -> etree._Element:
    box = question_text_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    enable_shrink_to_fit(clone)
    return clone
