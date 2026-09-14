"""Clone body text and one picture into fixed layout boxes."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.title_body_single_image.constants import (
    body_textbox_for,
    image_textbox_for,
)
from app.dynamic_rendering.services.format_layout.shared.image_resizer import fit_image_to_box
from app.dynamic_rendering.services.format_layout.shared.text_layout import configure_body_text_layout
from app.dynamic_rendering.utils.xml.shape_mutators import clone_and_place


def format_body(body_shape_el: etree._Element, dspec=None) -> etree._Element:
    box = body_textbox_for(dspec)
    off = (box["x"], box["y"])
    ext = (box["width"], box["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    configure_body_text_layout(clone)
    return clone


def format_image(
    picture_el: etree._Element, image_width_px: int, image_height_px: int, dspec=None
) -> etree._Element:
    box = image_textbox_for(dspec)
    fitted = fit_image_to_box(image_width_px, image_height_px, box)
    off = (fitted["x"], fitted["y"])
    ext = (fitted["width"], fitted["height"])
    return clone_and_place(picture_el, off, ext)
