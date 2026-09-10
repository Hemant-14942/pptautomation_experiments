"""Format title + images only slides.

Heading pill is left unchanged. Content images are placed below the heading
in the fixed content area using the same grid rules as image_only.
"""

from lxml import etree

from app.core.fit_layout.layout_formatter.image_only.image_resizer import fit_image_to_box
from app.core.template_converter.xml_utils import clone_and_place

from .constants import get_title_image_boxes


def format_images(
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
    layout: str = "balanced",
) -> list[etree._Element]:
    image_boxes = get_title_image_boxes(len(picture_els), layout=layout)
    clones = []
    for pic_el, (img_w, img_h), box in zip(picture_els, image_sizes, image_boxes):
        fitted = fit_image_to_box(img_w, img_h, box)
        off = (fitted["x"], fitted["y"])
        ext = (fitted["width"], fitted["height"])
        clones.append(clone_and_place(pic_el, off, ext))
    return clones


def format_title_image_only_slide(
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
    layout: str = "balanced",
) -> list[etree._Element]:
    return format_images(picture_els, image_sizes, layout=layout)
