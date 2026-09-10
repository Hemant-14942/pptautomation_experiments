"""Format a body_only slide.

What this does (in plain English):
  1. Copy the body text shape from the input slide.
  2. Move it into one big full-width text box (see constants.py).
  3. Turn on text wrapping so long lines break to the next line.
  4. Center the text vertically inside the box (equal space top and bottom).
  5. Tell PowerPoint to shrink the font if the text still does not fit.

PowerPoint stores each text box as XML. The part we edit looks like this:

  p:sp                          ← one shape on the slide (the text box)
    p:spPr
      a:xfrm
        a:off  x="..." y="..."  ← WHERE the box sits (left, top)
        a:ext  cx="..." cy="..."← HOW BIG the box is (width, height)
    p:txBody                      ← the text content area
      a:bodyPr
        wrap="square"             ← text wraps to next line
        anchor="ctr"              ← text block is centered top-to-bottom
        a:normAutofit             ← shrink font if text overflows
      a:p                         ← one paragraph
        a:pPr algn="l"            ← paragraph aligned to the left
        a:r                         ← one text run
          a:t  "Hello world"        ← the actual text characters
"""

from lxml import etree

from app.core.template_converter.xml_utils import (
    clone_and_place,
    enable_shrink_to_fit,
    enable_text_wrapping,
)
from app.utils.xml_helpers import q

from .constants import BODY_TEXTBOX


def set_vertical_center_anchor(el: etree._Element) -> None:
    """Center the text block vertically inside the text box.

    PowerPoint XML we change:
      p:txBody
        a:bodyPr anchor="ctr"   ← "ctr" = center vertically

    Whether the text is 2 lines or 10 lines, PowerPoint keeps equal
    empty space above and below the text block.
    """
    # Find the text body container inside the shape
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        return

    # Find the body properties tag — this controls how text sits in the box
    bodyPr = txBody.find(q("a:bodyPr"))
    if bodyPr is None:
        return

    # "ctr" means center — text floats in the middle of the box height
    bodyPr.set("anchor", "ctr")


def format_body_text(body_shape_el: etree._Element) -> etree._Element:
    """Clone the input body text shape and place it in the fixed full-slide box.

    Args:
        body_shape_el: the XML element (<p:sp>) of the body text shape
                       taken from the input slide.

    Returns:
        A new cloned shape, already positioned and configured.
    """
    # Step 1 — read the target position and size from constants
    off = (BODY_TEXTBOX["x"], BODY_TEXTBOX["y"])
    ext = (BODY_TEXTBOX["width"], BODY_TEXTBOX["height"])

    # Step 2 — deep-copy the shape and set its new position + size in XML
    #          (updates a:off and a:ext inside a:xfrm)
    clone = clone_and_place(body_shape_el, off, ext)

    # Step 3 — turn on line wrapping and left alignment
    #          (sets wrap="square", anchor="t", algn="l" on paragraphs)
    enable_text_wrapping(clone)

    # Step 4 — override vertical anchor to center (replaces the "t" from step 3)
    set_vertical_center_anchor(clone)

    # Step 5 — add normAutofit so PowerPoint shrinks font on overflow
    enable_shrink_to_fit(clone)

    return clone
