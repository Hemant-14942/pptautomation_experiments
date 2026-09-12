"""Clone and place question + image + MCQ shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import is_group
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_image_mcq.constants import (
    IMAGE_BOX,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)
from app.dynamic_rendering.services.format_layout.shared.mcq_option_layout import option_layout_for
from app.dynamic_rendering.services.format_layout.shared.image_resizer import fit_image_to_box
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


def format_image(
    picture_el: etree._Element, image_width_px: int, image_height_px: int
) -> etree._Element:
    fitted = fit_image_to_box(image_width_px, image_height_px, IMAGE_BOX)
    off = (fitted["x"], fitted["y"])
    ext = (fitted["width"], fitted["height"])
    return clone_and_place(picture_el, off, ext)


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
    return _format_wrapped_autofit_text(text_el, option_layout_for(option_idx)["text_box"])
