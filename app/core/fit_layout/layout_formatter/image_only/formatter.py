"""Format an image_only slide — pictures only, no text.

What this does (in plain English):
  1. Count how many content images are on the slide (1, 2, 3, 4, ...).
  2. Split the slide into slot boxes (grid layout from constants.py).
  3. For each picture: scale it to fit its slot, keep aspect ratio, center it.
  4. Return cloned picture shapes ready to put on the output slide.

PowerPoint XML we edit for each picture:

  p:pic                         <- one picture shape on the slide
    p:spPr
      a:xfrm
        a:off  x="..." y="..."  <- WHERE the picture sits (we set this)
        a:ext  cx="..." cy="..."<- HOW BIG the picture is (we set this)
    p:blipFill                    <- the actual image file (we do NOT touch this)
"""

from lxml import etree

from app.core.template_converter.xml_utils import clone_and_place

from .constants import get_image_boxes
from .image_resizer import fit_image_to_box


def format_images(
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
    layout: str = "balanced",
) -> list[etree._Element]:
    """Clone and position every picture into its grid slot.

    Args:
        picture_els:  list of picture XML elements from the input slide
        image_sizes:  list of (width_px, height_px) for each picture
        layout:       "balanced" (default) or "bottom_left" for 3-image slides

    Returns:
        list of cloned picture elements, same order as input
    """
    # Step 1 — ask constants how many boxes we need (1, 2, 3, 4, or grid)
    image_boxes = get_image_boxes(len(picture_els), layout=layout)

    clones = []
    # Step 2 — pair each picture with its slot box and pixel size
    for pic_el, (img_w, img_h), box in zip(picture_els, image_sizes, image_boxes):
        # Step 3 — scale picture to fit inside box (aspect ratio kept)
        fitted = fit_image_to_box(img_w, img_h, box)
        off = (fitted["x"], fitted["y"])
        ext = (fitted["width"], fitted["height"])
        # Step 4 — copy picture XML and set new position + size
        clone = clone_and_place(pic_el, off, ext)
        clones.append(clone)

    return clones


def format_image_only_slide(
    picture_els: list[etree._Element],
    image_sizes: list[tuple[int, int]],
    layout: str = "balanced",
) -> list[etree._Element]:
    """Main entry point — format all pictures on an image_only slide.

    Args:
        picture_els:  picture XML elements from input slide
        image_sizes:  pixel sizes for each picture
        layout:       grid style for 3 images (see constants.py)

    Returns:
        list of positioned picture clones for the output slide
    """
    return format_images(picture_els, image_sizes, layout=layout)
