"""Format question pill + question text only slides (no table, no MCQ).

Question text: wrap first, then normAutofit. Top-left aligned — text starts
at the top of the box, just below the question pill.
"""

from lxml import etree

from app.core.template_converter.xml_utils import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
)
from app.utils.xml_helpers import q

from .constants import QUESTION_LABEL, QUESTION_PILL, QUESTION_TEXT


def _set_text(el: etree._Element, text: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        return
    t_el = txBody.find(f".//{q('a:t')}")
    if t_el is not None:
        t_el.text = text


def format_question_pill(pill_el: etree._Element) -> etree._Element:
    off = (QUESTION_PILL["x"], QUESTION_PILL["y"])
    ext = (QUESTION_PILL["width"], QUESTION_PILL["height"])
    return clone_and_place(pill_el, off, ext)


def format_question_label(label_el: etree._Element, label_text: str = "Question") -> etree._Element:
    off = (QUESTION_LABEL["x"], QUESTION_LABEL["y"])
    ext = (QUESTION_LABEL["width"], QUESTION_LABEL["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, label_text)
    return clone


def format_question_text(text_el: etree._Element) -> etree._Element:
    """Place question text below pill — wrap, top-left, normAutofit on overflow."""
    off = (QUESTION_TEXT["x"], QUESTION_TEXT["y"])
    ext = (QUESTION_TEXT["width"], QUESTION_TEXT["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)   # wrap + anchor top-left
    enable_shrink_to_fit(clone)   # shrink font if wrapped text too tall
    return clone
