"""Clone body text and one picture into fixed layout boxes."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.title_body_single_image.constants import (
    BODY_TEXTBOX,
    IMAGE_TEXTBOX,
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


def format_image(
    picture_el: etree._Element, image_width_px: int, image_height_px: int
) -> etree._Element:
    fitted = fit_image_to_box(image_width_px, image_height_px, IMAGE_TEXTBOX)
    off = (fitted["x"], fitted["y"])
    ext = (fitted["width"], fitted["height"])
    return clone_and_place(picture_el, off, ext)
