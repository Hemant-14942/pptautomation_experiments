"""Shared formatters for question pill + label shapes."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.shared.qpill_layout import (
    question_label_for,
    question_pill_for,
)
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import clone_and_place


def _set_text(el: etree._Element, text: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return
    t_el = txBody.find(f".//{q('a:t')}")
    if t_el is not None:
        t_el.text = text


def format_question_pill(pill_el: etree._Element, dspec=None) -> etree._Element:
    box = question_pill_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    return clone_and_place(pill_el, off, ext)


def format_question_label(
    label_el: etree._Element,
    label_text: str = "Question",
    dspec=None,
) -> etree._Element:
    box = question_label_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, label_text)
    return clone
