"""Clone body text and multiple pictures into fixed layout boxes."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.title_body_multiple_images.constants import (
    BODY_TEXTBOX,
    get_image_boxes,
)
from app.dynamic_rendering.services.format_layout.shared.image_resizer import fit_image_to_box
from app.dynamic_rendering.services.format_layout.shared.text_layout import set_vertical_center_anchor
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
)


def format_body(body_shape_el: etree._Element) -> etree._Element:
    off = (BODY_TEXTBOX["x"], BODY_TEXTBOX["y"])
    ext = (BODY_TEXTBOX["width"], BODY_TEXTBOX["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    enable_text_wrapping(clone)
    set_vertical_center_anchor(clone)
    enable_shrink_to_fit(clone)
    return clone


def format_images(
    picture_els: list[etree._Element], image_sizes: list[tuple[int, int]]
) -> list[etree._Element]:
    image_boxes = get_image_boxes(len(picture_els))
    clones = []
    for pic_el, (img_w, img_h), box in zip(picture_els, image_sizes, image_boxes):
        fitted = fit_image_to_box(img_w, img_h, box)
        off = (fitted["x"], fitted["y"])
        ext = (fitted["width"], fitted["height"])
        clones.append(clone_and_place(pic_el, off, ext))
    return clones
