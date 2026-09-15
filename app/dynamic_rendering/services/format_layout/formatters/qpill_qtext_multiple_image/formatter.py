"""Clone and place question text + multiple images at fixed layout coordinates."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_multiple_image.constants import (
    image_boxes_for,
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
