"""Reposition an input slide's body text and multiple images into the
fixed title_body_multiple_images layout boxes.

Body text goes into the fixed left box. Images are distributed across
the stacked right-side boxes (2 images: 40% each; 3+ images: equal height).
"""

from lxml import etree

from app.core.template_converter.xml_utils import clone_and_place, enable_text_wrapping

from .constants import BODY_TEXTBOX, get_image_boxes
from .image_resizer import fit_image_to_box


def format_body(body_shape_el: etree._Element) -> etree._Element:
    """Clone the input slide's body text shape into BODY_TEXTBOX, wrap mode on."""
    # off take the starting (x,y) text box position where from to start cloning the text box
    off = (BODY_TEXTBOX["x"], BODY_TEXTBOX["y"])
    #  ext tell from that point of off how much extend to the height and width of the text box
    ext = (BODY_TEXTBOX["width"], BODY_TEXTBOX["height"])
    # clone the body shape element to the text box position and size with all the text content
    clone = clone_and_place(body_shape_el, off, ext)
    # enable the text wrapping for the cloned text box
    enable_text_wrapping(clone)
    return clone


def format_images(
    picture_els: list[etree._Element], image_sizes: list[tuple[int, int]]
) -> list[etree._Element]:
    """Clone and position each picture into its assigned image box.

    Args:
        picture_els: list of picture XML elements from the input slide
        image_sizes: list of (width_px, height_px) tuples, one per picture

    Returns:
        list of cloned, positioned picture elements, in the same order
    """
    image_boxes = get_image_boxes(len(picture_els))
    clones = []
    for pic_el, (img_w, img_h), box in zip(picture_els, image_sizes, image_boxes):
        fitted = fit_image_to_box(img_w, img_h, box)
        off = (fitted["x"], fitted["y"])
        ext = (fitted["width"], fitted["height"])
        clone = clone_and_place(pic_el, off, ext)
        clones.append(clone)
    return clones


def format_title_body_multiple_images(
    body_shape_el: etree._Element,
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
) -> tuple[etree._Element, list[etree._Element]]:
    """Return (body_clone, [picture_clone1, picture_clone2, ...]) positioned
    per the fixed layout, ready to be appended to the output slide's spTree."""
    body_clone = format_body(body_shape_el)
    picture_clones = format_images(picture_els, image_sizes)
    return body_clone, picture_clones
