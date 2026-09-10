"""Format question + text + table + MCQ slides (p.pptx slide 0 layout).

Text boxes (question + answers): wrap first, then normAutofit shrinks font
if wrapped text still does not fit in the box height.

Table: same size as input, centered in TABLE_BOX (no scaling).
"""

from lxml import etree

from app.core.template_converter.xml_utils import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
    place_group,
)
from app.core.fit_layout.layout_formatter.title_table_only.table_utils import (
    clone_and_place_table,
    get_table_total_height,
    get_table_width,
)
from app.utils.xml_helpers import local_name, q

from .constants import (
    MCQ_OPTIONS,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
    TABLE_BOX,
)


def is_group(el: etree._Element) -> bool:
    return local_name(el) == "grpSp"


def _set_text(el: etree._Element, text: str) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        return
    t_el = txBody.find(f".//{q('a:t')}")
    if t_el is not None:
        t_el.text = text


def _format_wrapped_autofit_text(text_el: etree._Element, box: dict[str, int]) -> etree._Element:
    """Place text in box with wrap on; normAutofit shrinks if still overflow."""
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)   # step 1: break lines at box width (no spill right)
    enable_shrink_to_fit(clone)   # step 2: shrink font if too many lines for box height
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
    """Place table in TABLE_BOX at same size — center if fits, else top-left."""
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
