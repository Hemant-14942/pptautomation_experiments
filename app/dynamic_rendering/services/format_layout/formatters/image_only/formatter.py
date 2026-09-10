"""Clone and position content pictures into grid slots."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.image_only.constants import get_image_boxes
from app.dynamic_rendering.services.format_layout.shared.image_resizer import fit_image_to_box
from app.dynamic_rendering.utils.xml.shape_mutators import clone_and_place


def format_images(
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
    layout: str = "balanced",
) -> list[etree._Element]:
    image_boxes = get_image_boxes(len(picture_els), layout=layout)
    clones = []
    for pic_el, (img_w, img_h), box in zip(picture_els, image_sizes, image_boxes):
        fitted = fit_image_to_box(img_w, img_h, box)
        off = (fitted["x"], fitted["y"])
        ext = (fitted["width"], fitted["height"])
        clones.append(clone_and_place(pic_el, off, ext))
    return clones
