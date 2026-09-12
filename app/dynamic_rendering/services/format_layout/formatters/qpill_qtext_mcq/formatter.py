"""Clone and place MCQ slide shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import is_group
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)
from app.dynamic_rendering.services.format_layout.shared.mcq_option_layout import option_layout_for
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
    place_group,
    set_text_center_align,
)


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
    off = (QUESTION_TEXT["x"], QUESTION_TEXT["y"])
    ext = (QUESTION_TEXT["width"], QUESTION_TEXT["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    enable_shrink_to_fit(clone)
    return clone


def format_mcq_option_pill(option_idx: int, pill_el: etree._Element) -> None | etree._Element:
    option = option_layout_for(option_idx)
    off = (option["pill"]["x"], option["pill"]["y"])
    ext = (option["pill"]["width"], option["pill"]["height"])

    if is_group(pill_el):
        place_group(pill_el, off, ext)
        return None

    return clone_and_place(pill_el, off, ext)


def format_mcq_option_label(option_idx: int, label_el: etree._Element) -> etree._Element:
    option = option_layout_for(option_idx)
    label_box = option["label_box"]
    off = (label_box["x"], label_box["y"])
    ext = (label_box["width"], label_box["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, option["label"])
    set_text_center_align(clone)
    return clone


def format_mcq_answer_text(option_idx: int, text_el: etree._Element) -> etree._Element:
    option = option_layout_for(option_idx)
    text_box = option["text_box"]
    off = (text_box["x"], text_box["y"])
    ext = (text_box["width"], text_box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    enable_shrink_to_fit(clone)
    return clone
