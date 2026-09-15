"""Clone and place question text + single image shapes at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_single_image.constants import (
    image_area_for,
    question_text_for,
)
from app.dynamic_rendering.services.format_layout.shared.image_resizer import fit_image_to_box
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


def format_image(
    pic_el: etree._Element, image_size: tuple[int, int], dspec=None
) -> etree._Element:
    box = image_area_for(dspec)
    fitted = fit_image_to_box(image_size[0], image_size[1], box)
    off = (fitted["x"], fitted["y"])
    ext = (fitted["width"], fitted["height"])
    return clone_and_place(pic_el, off, ext)
