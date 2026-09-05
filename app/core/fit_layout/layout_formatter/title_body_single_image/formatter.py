"""Reposition an input slide's body text and image into the fixed
title_body_single_image layout boxes.

The body text shape and the picture shape already exist (with their real
content) on the input slide — this does not build new XML from scratch, it
clones each shape into the fixed box for its role, reusing the same
clone-and-place pattern the rest of the template converter uses.
"""

from lxml import etree

from app.core.template_converter.xml_utils import clone_and_place, enable_text_wrapping

from .constants import BODY_TEXTBOX, IMAGE_TEXTBOX
from .image_resizer import fit_image_to_box


def format_body(body_shape_el: etree._Element) -> etree._Element:
    """Clone the input slide's body text shape into BODY_TEXTBOX, wrap mode on."""
    off = (BODY_TEXTBOX["x"], BODY_TEXTBOX["y"])
    ext = (BODY_TEXTBOX["width"], BODY_TEXTBOX["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    enable_text_wrapping(clone)
    return clone


def format_image(
    picture_el: etree._Element, image_width_px: int, image_height_px: int
) -> etree._Element:
    """Clone the input slide's picture shape into IMAGE_TEXTBOX, resized
    (aspect-ratio preserved) only as much as needed to fit."""
    fitted = fit_image_to_box(image_width_px, image_height_px, IMAGE_TEXTBOX)
    off = (fitted["x"], fitted["y"])
    ext = (fitted["width"], fitted["height"])
    return clone_and_place(picture_el, off, ext)


def format_title_body_single_image(
    body_shape_el: etree._Element,
    picture_el: etree._Element,
    image_width_px: int,
    image_height_px: int,
) -> tuple[etree._Element, etree._Element]:
    """Return (body_clone, picture_clone) positioned per the fixed layout,
    ready to be appended to the output slide's spTree."""
    body_clone = format_body(body_shape_el)
    picture_clone = format_image(picture_el, image_width_px, image_height_px)
    return body_clone, picture_clone
