"""Clone and place question + table + MCQ shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import is_group
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_table_mcq.constants import (
    MCQ_OPTIONS,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
    TABLE_BOX,
)
from app.dynamic_rendering.services.format_layout.shared.table_utils import (
    clone_and_place_table,
    get_table_total_height,
    get_table_width,
)
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
    place_group,
)


def _set_text(el: etree._Element, text: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        return
    t_el = txBody.find(f".//{q('a:t')}")
    if t_el is not None:
        t_el.text = text


def _format_wrapped_autofit_text(text_el: etree._Element, box: dict[str, int]) -> etree._Element:
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    enable_shrink_to_fit(clone)
    return clone


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
    return _format_wrapped_autofit_text(text_el, QUESTION_TEXT)


def format_table(graphic_frame_el: etree._Element) -> etree._Element:
    table_height = get_table_total_height(graphic_frame_el)
    table_width = get_table_width(graphic_frame_el)
    if table_height <= TABLE_BOX["height"]:
        y = TABLE_BOX["y"] + (TABLE_BOX["height"] - table_height) // 2
    else:
        y = TABLE_BOX["y"]
    if table_width <= TABLE_BOX["width"]:
        x = TABLE_BOX["x"] + (TABLE_BOX["width"] - table_width) // 2
    else:
        x = TABLE_BOX["x"]
    return clone_and_place_table(graphic_frame_el, (x, y))


def format_mcq_option_pill(option_idx: int, pill_el: etree._Element) -> None | etree._Element:
    option = MCQ_OPTIONS[option_idx]
    off = (option["pill"]["x"], option["pill"]["y"])
    ext = (option["pill"]["width"], option["pill"]["height"])
    if is_group(pill_el):
        place_group(pill_el, off, ext)
        return None
    return clone_and_place(pill_el, off, ext)


def format_mcq_option_label(option_idx: int, label_el: etree._Element) -> etree._Element:
    option = MCQ_OPTIONS[option_idx]
    label_box = option["label_box"]
    off = (label_box["x"], label_box["y"])
    ext = (label_box["width"], label_box["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, option["label"])
    return clone


def format_mcq_answer_text(option_idx: int, text_el: etree._Element) -> etree._Element:
    return _format_wrapped_autofit_text(text_el, MCQ_OPTIONS[option_idx]["text_box"])
