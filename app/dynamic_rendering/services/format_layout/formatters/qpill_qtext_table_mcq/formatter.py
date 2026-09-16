"""Clone and place question + table + MCQ shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import is_group
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_table_mcq.constants import (
    mcq_options_for,
    question_text_for,
    table_box_for,
)
from app.dynamic_rendering.services.format_layout.shared.mcq_option_layout import option_layout_from_options
from app.dynamic_rendering.services.format_layout.shared.qpill_formatters import (
    format_question_label,
    format_question_pill,
)
from app.dynamic_rendering.services.format_layout.shared.table_utils import format_table_in_box
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
    place_group,
    set_text_center_align,
)
from app.dynamic_rendering.utils.xml.helpers import q


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


def _option_layout(option_idx: int, dspec=None) -> dict:
    # Defence template: options already come back in a 2-column grid from
    # mcq_options_for(); pass columns=2 so extrapolated rows beyond D (E, F, ...)
    # continue the grid instead of stacking straight down. Every other
    # template: columns=1, the original single-column extrapolation.
    columns = 2 if dspec is not None and dspec.has_top_banner() else 1
    return option_layout_from_options(option_idx, mcq_options_for(dspec), columns=columns)


def format_question_text(text_el: etree._Element, dspec=None) -> etree._Element:
    return _format_wrapped_autofit_text(text_el, question_text_for(dspec))


def format_table(graphic_frame_el: etree._Element, dspec=None) -> etree._Element:
    return format_table_in_box(graphic_frame_el, table_box_for(dspec))


def format_mcq_option_pill(
    option_idx: int, pill_el: etree._Element, dspec=None
) -> None | etree._Element:
    option = _option_layout(option_idx, dspec)
    off = (option["pill"]["x"], option["pill"]["y"])
    ext = (option["pill"]["width"], option["pill"]["height"])
    if is_group(pill_el):
        place_group(pill_el, off, ext)
        return None
    return clone_and_place(pill_el, off, ext)


def format_mcq_option_label(
    option_idx: int, label_el: etree._Element, dspec=None
) -> etree._Element:
    option = _option_layout(option_idx, dspec)
    label_box = option["label_box"]
    off = (label_box["x"], label_box["y"])
    ext = (label_box["width"], label_box["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, option["label"])
    set_text_center_align(clone)
    return clone


def format_mcq_answer_text(option_idx: int, text_el: etree._Element, dspec=None) -> etree._Element:
    return _format_wrapped_autofit_text(text_el, _option_layout(option_idx, dspec)["text_box"])
