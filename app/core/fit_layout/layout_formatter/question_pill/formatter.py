
from lxml import etree

from app.core.template_converter.xml_utils import clone_and_place
from app.utils.xml_helpers import q

from .constants import QUESTION_PILL, QUESTION_LABEL, QUESTION_BODY


def format_question_pill(pill_el: etree._Element, label_text: str) -> etree._Element:
    """Clone the question pill shape and position it at the fixed location.

    The pill shape is cloned from the input slide, then repositioned and resized
    to the fixed layout position defined in constants.py. The text inside the pill
    is also updated with the new label text.

    Args:
        pill_el: The pill shape element cloned from the input slide (XML element).
        label_text: Text to display inside the pill (string like "Question" or "Option A").

    Returns:
        The cloned pill shape element, positioned at fixed coordinates with label text updated.
    """

    # Extract the X and Y position values from QUESTION_PILL constant
    # These define where the left-top corner of the pill should be placed
    # Example: (-1864528, 681774) means -2.039" left, 0.746" from top
    off = (QUESTION_PILL["x"], QUESTION_PILL["y"])

    # Extract the width and height values from QUESTION_PILL constant
    # These define how big the pill shape should be
    # Example: (7081988, 1569660) means 7.745" wide, 1.717" tall
    ext = (QUESTION_PILL["width"], QUESTION_PILL["height"])

    # Call clone_and_place() to:
    # 1. Make a copy of the pill shape from the input slide
    # 2. Move it to the fixed position (off = x,y coordinates)
    # 3. Resize it to the fixed size (ext = width,height)
    # The original pill_el stays unchanged, only the copy is modified
    pill_clone = clone_and_place(pill_el, off, ext)

    # Extract the X and Y position for the label text box from QUESTION_LABEL constant
    # The label text box sits INSIDE the pill and contains the actual text
    # Example: (1039500, 827049) means 1.137" left, 0.904" from top
    label_off = (QUESTION_LABEL["x"], QUESTION_LABEL["y"])

    # Extract the width and height for the label text box from QUESTION_LABEL constant
    # Example: (4562190, 1015622) means 4.989" wide, 1.111" tall
    label_ext = (QUESTION_LABEL["width"], QUESTION_LABEL["height"])

    # ============================================================================
    # IMPORTANT: PowerPoint XML Structure for Text
    # ============================================================================
    # The text inside a shape is stored in this nested structure:
    #
    # <p:sp>                          (the shape element)
    #   <p:txBody>                    (or <a:txBody> - container for text)
    #     <a:p>                       (paragraph - a line of text)
    #       <a:r>                     (run - a piece of text with same formatting)
    #         <a:t>The actual text here</a:t>   (the text element - contains the string)
    #
    # We need to find the <a:t> element and change its text content.
    # ============================================================================

    # Search inside the cloned pill shape for the text body element
    # PowerPoint stores text inside a <p:txBody> or <a:txBody> element
    # The q() function converts "p:txBody" into the full XML namespace name
    # If found, txBody will point to that element; if not found, txBody = None
    txBody = pill_clone.find(q("p:txBody"))

    # If we didn't find <p:txBody>, try the alternative namespace <a:txBody>
    # Some PowerPoint elements use different namespaces for the same thing
    # We check both to be safe - one of them should exist
    if txBody is None:
        txBody = pill_clone.find(q("a:txBody"))

    # Only proceed if we found a text body element (either p:txBody or a:txBody)
    # If neither exists, the pill has no text and we skip the text update
    if txBody is not None:
        # Search inside the text body to find the actual text element <a:t>
        # This element contains the text string we want to change
        # The search finds the FIRST <a:t> element (usually that's all there is)
        t_el = txBody.find(q("a:t"))

        # Only update the text if we found the text element
        # If it doesn't exist, we can't change the text
        if t_el is not None:
            # Replace the old text with the new label text
            # This is where "Question" or "Option A" actually gets set
            # Examples: t_el.text = "Question", or t_el.text = "Option B"
            t_el.text = label_text

    # Return the cloned pill shape with:
    # 1. New position (from QUESTION_PILL constants)
    # 2. New size (from QUESTION_PILL constants)
    # 3. Updated text (from label_text parameter)
    # The caller will add this to the output slide's shape collection
    return pill_clone


def format_question_body_text(body_el: etree._Element) -> etree._Element:
    """Clone the question body text and position it at the fixed location.

    The question body text box (e.g., "Find the cofactors of A") is cloned from
    the input slide and repositioned to the fixed layout location below the pill.
    Text wrapping is enabled so long questions wrap to multiple lines.

    Args:
        body_el: The body text shape element from the input slide (XML element).

    Returns:
        The cloned body text element, positioned at fixed coordinates.
    """

    # Extract the X and Y position values from QUESTION_BODY constant
    # These define where the left-top corner of the body text box should be placed
    # Example: (1104806, 2396709) means 1.208" left, 2.621" from top (below the pill)
    off = (QUESTION_BODY["x"], QUESTION_BODY["y"])

    # Extract the width and height values from QUESTION_BODY constant
    # These define how big the body text box should be
    # Example: (34747200, 3474720) means 38.0" wide, 3.8" tall
    ext = (QUESTION_BODY["width"], QUESTION_BODY["height"])

    # Call clone_and_place() to:
    # 1. Make a copy of the body text box from the input slide
    # 2. Move it to the fixed position (off = x,y coordinates)
    # 3. Resize it to the fixed size (ext = width,height)
    # The original body_el stays unchanged, only the copy is modified
    body_clone = clone_and_place(body_el, off, ext)

    # Enable text wrapping so the question text wraps to multiple lines
    # instead of being cut off or making the text box overflow
    # ============================================================================
    # Text wrapping configuration involves finding the text body (<p:txBody>)
    # and setting wrap="square" so text flows within the box boundaries
    # ============================================================================
    txBody = body_clone.find(q("p:txBody"))
    if txBody is None:
        txBody = body_clone.find(q("a:txBody"))

    # Only enable wrapping if we found the text body element
    if txBody is not None:
        # Find the bodyPr element that controls text box properties
        bodyPr = txBody.find(q("a:bodyPr"))
        if bodyPr is not None:
            # Set wrap="square" to enable text wrapping within the box boundaries
            # This allows multi-line questions to display properly
            bodyPr.set("wrap", "square")
            # Set anchor="t" to anchor text at the top of the box
            # (not centered or at bottom)
            bodyPr.set("anchor", "t")

    # Return the cloned body text with:
    # 1. New position (from QUESTION_BODY constants)
    # 2. New size (from QUESTION_BODY constants)
    # 3. Text wrapping enabled for multi-line display
    # The caller will add this to the output slide's shape collection
    return body_clone
