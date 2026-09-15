"""Clone and place question + image + MCQ shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import is_group
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_image_mcq.constants import (
    LEFT_ANSWER_WIDTH_EMU,
    image_boxes_for,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
    question_text_for,
)
from app.dynamic_rendering.services.format_layout.shared.image_resizer import fit_image_to_box
from app.dynamic_rendering.services.format_layout.shared.mcq_option_layout import option_layout_for
from app.dynamic_rendering.services.format_layout.shared.qpill_formatters import (
    format_question_label,
    format_question_pill,
)
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


def format_question_text(text_el: etree._Element, dspec=None) -> etree._Element:
    box = question_text_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    enable_shrink_to_fit(clone)
    return clone


def format_images(
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
    dspec=None,
) -> list[etree._Element]:
    image_boxes = image_boxes_for(len(picture_els), dspec)
    clones = []
    for pic_el, (img_w, img_h), box in zip(picture_els, image_sizes, image_boxes):
        fitted = fit_image_to_box(img_w, img_h, box)
        off = (fitted["x"], fitted["y"])
        ext = (fitted["width"], fitted["height"])
        clones.append(clone_and_place(pic_el, off, ext))
    return clones


def format_mcq_option_pill(
    option_idx: int, pill_el: etree._Element, dspec=None
) -> None | etree._Element:
    option = option_layout_for(option_idx, dspec)
    off = (option["pill"]["x"], option["pill"]["y"])
    ext = (option["pill"]["width"], option["pill"]["height"])
    if is_group(pill_el):
        place_group(pill_el, off, ext)
        return None
    return clone_and_place(pill_el, off, ext)


def format_mcq_option_label(
    option_idx: int, label_el: etree._Element, dspec=None
) -> etree._Element:
    option = option_layout_for(option_idx, dspec)
    label_box = option["label_box"]
    off = (label_box["x"], label_box["y"])
    ext = (label_box["width"], label_box["height"])
    clone = clone_and_place(label_el, off, ext)
    _set_text(clone, option["label"])
    set_text_center_align(clone)
    return clone


def format_mcq_answer_text(option_idx: int, text_el: etree._Element, dspec=None) -> etree._Element:
    option = option_layout_for(option_idx, dspec)
    text_box = dict(option["text_box"])
    text_box["width"] = LEFT_ANSWER_WIDTH_EMU
    off = (text_box["x"], text_box["y"])
    ext = (text_box["width"], text_box["height"])
    clone = clone_and_place(text_el, off, ext)
    enable_text_wrapping(clone)
    enable_shrink_to_fit(clone)
    return clone
