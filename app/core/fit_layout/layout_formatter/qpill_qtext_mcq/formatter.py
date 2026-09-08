"""Format complete MCQ slides: question pill + text + four options.

Reposition each input shape to the fixed coordinates in constants.py
(extracted from p.pptx slide 29). Two shape kinds show up on the input:

- Plain shapes (<p:sp>) -- cloned via clone_and_place(), then the
  original is removed from the tree and the repositioned clone appended
  (same remove+append convention as title_body_only).
- Grouped pill+label (<p:grpSp>, options B/C/D in the source deck) --
  moved in place via place_group(), a pure rigid-body translation that
  leaves the pill and its nested label exactly where the designer put
  them relative to each other. No clone/remove/append needed for these.
"""

from lxml import etree

from app.core.template_converter.xml_utils import (
    clone_and_place,
    enable_text_wrapping,
    place_group,
)
from app.utils.xml_helpers import local_name, q

from .constants import (
    MCQ_OPTIONS,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)


def is_group(el: etree._Element) -> bool:
    """True if el is a <p:grpSp> (group of shapes), not a plain <p:sp>."""
    return local_name(el) == "grpSp"


def _set_text(el: etree._Element, text: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        return
    t_el = txBody.find(f".//{q('a:t')}")
    if t_el is not None:
        t_el.text = text


def format_question_pill(pill_el: etree._Element) -> etree._Element:
    """Clone and position the question pill at the fixed top location."""
    off = (QUESTION_PILL["x"], QUESTION_PILL["y"])
    ext = (QUESTION_PILL["width"], QUESTION_PILL["height"])
    return clone_and_place(pill_el, off, ext)


def format_question_label(label_el: etree._Element, label_text: str = "Question") -> etree._Element:
    """Clone and position the question label text inside the pill."""
    off = (QUESTION_LABEL["x"], QUESTION_LABEL["y"])
    ext = (QUESTION_LABEL["width"], QUESTION_LABEL["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, label_text)
    return clone


def format_question_text(text_el: etree._Element) -> etree._Element:
    """Clone and position the question text box below the pill, wrapped
    and left-aligned. Multi-line questions display top-anchored."""
    off = (QUESTION_TEXT["x"], QUESTION_TEXT["y"])
    ext = (QUESTION_TEXT["width"], QUESTION_TEXT["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    return clone


def format_mcq_option_pill(option_idx: int, pill_el: etree._Element) -> None | etree._Element:
    """Reposition one MCQ option's pill (+ its nested label, if grouped).

    Groups are translated in place (returns None -- nothing to
    remove/append, the original element is already mutated).
    Plain shapes are cloned + positioned (caller must remove the
    original and append the returned clone).
    """
    option = MCQ_OPTIONS[option_idx]
    off = (option["pill"]["x"], option["pill"]["y"])
    ext = (option["pill"]["width"], option["pill"]["height"])

    if is_group(pill_el):
        place_group(pill_el, off, ext)
        return None

    return clone_and_place(pill_el, off, ext)


def format_mcq_option_label(option_idx: int, label_el: etree._Element) -> etree._Element:
    """Clone and position a standalone option label (only used for
    options whose pill isn't grouped with its label, e.g. option A)."""
    option = MCQ_OPTIONS[option_idx]
    label_box = option["label_box"]
    off = (label_box["x"], label_box["y"])
    ext = (label_box["width"], label_box["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, option["label"])
    return clone


def format_mcq_answer_text(option_idx: int, text_el: etree._Element) -> etree._Element:
    """Clone and position the answer text box to the right of the pill,
    wrapped and left-aligned, full remaining slide width."""
    option = MCQ_OPTIONS[option_idx]
    text_box = option["text_box"]
    off = (text_box["x"], text_box["y"])
    ext = (text_box["width"], text_box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    return clone
