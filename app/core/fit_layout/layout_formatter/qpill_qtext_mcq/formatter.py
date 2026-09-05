"""Format complete MCQ slides: question pill + text + four options.

This formatter handles the full MCQ slide layout:
1. Question pill shape with label
2. Question text box (can be multi-line)
3. Four MCQ option pills (A, B, C, D) with answer text for each

All positions are fixed according to constants.py extracted from p.pptx slide 24.
"""

from lxml import etree

from app.core.template_converter.xml_utils import clone_and_place
from app.utils.xml_helpers import q

from .constants import (
    MCQ_OPTIONS,
    OPTION_A_LABEL,
    OPTION_A_PILL,
    OPTION_A_TEXT,
    OPTION_B_LABEL,
    OPTION_B_PILL,
    OPTION_B_TEXT,
    OPTION_C_LABEL,
    OPTION_C_PILL,
    OPTION_C_TEXT,
    OPTION_D_LABEL,
    OPTION_D_PILL,
    OPTION_D_TEXT,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)


def format_question_pill(pill_el: etree._Element, label_text: str = "Question") -> etree._Element:
    """Clone and position the question pill at the fixed top location.

    The pill is a rounded rectangle shape that appears at the very top of the slide.
    The label text sits inside the pill.

    Args:
        pill_el: The question pill shape element (AUTO_SHAPE, roundRect)
        label_text: Text to display in the pill (default: "Question")

    Returns:
        Cloned pill positioned at fixed location with label text set
    """
    # Extract fixed position from constants for the pill shape
    # Position: (-2.039", 0.746")
    pill_off = (QUESTION_PILL["x"], QUESTION_PILL["y"])
    # Extract fixed size from constants
    # Size: (7.745", 1.717")
    pill_ext = (QUESTION_PILL["width"], QUESTION_PILL["height"])

    # Clone the pill shape and position it at fixed coordinates
    pill_clone = clone_and_place(pill_el, pill_off, pill_ext)

    # Extract fixed position for the label text inside the pill
    label_off = (QUESTION_LABEL["x"], QUESTION_LABEL["y"])
    # Extract fixed size for the label text
    label_ext = (QUESTION_LABEL["width"], QUESTION_LABEL["height"])

    # If the pill element contains text, we could position it here
    # For now, the label is a separate element handled by format_question_label()

    # Return the cloned and positioned pill
    return pill_clone


def format_question_label(label_el: etree._Element, label_text: str = "Question") -> etree._Element:
    """Clone and position the question label text inside the pill.

    Args:
        label_el: The label text box element
        label_text: Text to display (default: "Question")

    Returns:
        Cloned label positioned inside pill with text set
    """
    # Extract fixed position for the label (inside pill)
    # Position: (1.137", 0.904")
    label_off = (QUESTION_LABEL["x"], QUESTION_LABEL["y"])
    # Extract fixed size for the label
    # Size: (4.989", 1.111")
    label_ext = (QUESTION_LABEL["width"], QUESTION_LABEL["height"])

    # Clone the label and position it inside the pill
    label_clone = clone_and_place(label_el, label_off, label_ext)

    # Update the text content in the cloned label
    txBody = label_clone.find(q("p:txBody"))
    if txBody is None:
        txBody = label_clone.find(q("a:txBody"))

    if txBody is not None:
        # Find the text element inside the label
        t_el = txBody.find(q("a:t"))
        # Update it with the provided label text
        if t_el is not None:
            t_el.text = label_text

    # Return the cloned and positioned label
    return label_clone


def format_question_text(text_el: etree._Element) -> etree._Element:
    """Clone and position the question text box below the pill.

    The question text box appears below the pill with a gap and can contain
    multi-line text (4-5 lines). Text wrapping is enabled.

    Args:
        text_el: The question text box element

    Returns:
        Cloned question text positioned below pill with wrapping enabled
    """
    # Extract fixed position for the question text box
    # Position: (1.208", 2.621") — below the pill
    text_off = (QUESTION_TEXT["x"], QUESTION_TEXT["y"])
    # Extract fixed size for the question text box
    # Size: (38.0", 2.8") — full width-ish, room for multiple lines
    text_ext = (QUESTION_TEXT["width"], QUESTION_TEXT["height"])

    # Clone the text box and position it at fixed coordinates
    text_clone = clone_and_place(text_el, text_off, text_ext)

    # Enable text wrapping so multi-line questions display properly
    txBody = text_clone.find(q("p:txBody"))
    if txBody is None:
        txBody = text_clone.find(q("a:txBody"))

    if txBody is not None:
        # Find the bodyPr element that controls text wrapping
        bodyPr = txBody.find(q("a:bodyPr"))
        if bodyPr is not None:
            # Enable square text wrapping (text wraps within box boundaries)
            bodyPr.set("wrap", "square")
            # Anchor text at top (not centered or at bottom)
            bodyPr.set("anchor", "t")

    # Return the cloned text with wrapping enabled
    return text_clone


def format_mcq_option(
    option_idx: int,
    pill_el: etree._Element,
    label_el: etree._Element,
    text_el: etree._Element,
) -> tuple[etree._Element, etree._Element, etree._Element]:
    """Clone and position one MCQ option (A, B, C, or D).

    Each option has three parts:
    1. Pill shape (ellipse) on the left
    2. Label text ("A", "B", "C", "D") inside the pill
    3. Answer text box to the right of the pill

    Args:
        option_idx: Option index (0=A, 1=B, 2=C, 3=D)
        pill_el: The option pill shape element (ellipse)
        label_el: The option label text element
        text_el: The option answer text element

    Returns:
        Tuple of (pill_clone, label_clone, text_clone) all positioned
    """
    # Get the constants for this option (A, B, C, or D)
    option = MCQ_OPTIONS[option_idx]

    # Format the pill (ellipse shape)
    # =========================================================================
    # Extract position and size from constants for this option's pill
    pill_off = (option["pill"]["x"], option["pill"]["y"])
    pill_ext = (option["pill"]["width"], option["pill"]["height"])
    # Clone and position the pill
    pill_clone = clone_and_place(pill_el, pill_off, pill_ext)

    # Format the label (option letter: A, B, C, D)
    # =========================================================================
    # Extract position and size from constants for this option's label
    label_off = (option["label_box"]["x"], option["label_box"]["y"])
    label_ext = (option["label_box"]["width"], option["label_box"]["height"])
    # Clone and position the label
    label_clone = clone_and_place(label_el, label_off, label_ext)

    # Update the label text with the option letter (A, B, C, D)
    txBody = label_clone.find(q("p:txBody"))
    if txBody is None:
        txBody = label_clone.find(q("a:txBody"))

    if txBody is not None:
        t_el = txBody.find(q("a:t"))
        if t_el is not None:
            # Set the text to the option label (A, B, C, or D)
            t_el.text = option["label"]

    # Format the answer text (to the right of the pill)
    # =========================================================================
    # Extract position and size from constants for this option's answer text
    text_off = (option["text_box"]["x"], option["text_box"]["y"])
    text_ext = (option["text_box"]["width"], option["text_box"]["height"])
    # Clone and position the answer text
    text_clone = clone_and_place(text_el, text_off, text_ext)

    # Enable text wrapping for the answer text (in case it's long)
    txBody = text_clone.find(q("p:txBody"))
    if txBody is None:
        txBody = text_clone.find(q("a:txBody"))

    if txBody is not None:
        bodyPr = txBody.find(q("a:bodyPr"))
        if bodyPr is not None:
            bodyPr.set("wrap", "square")
            bodyPr.set("anchor", "t")

    # Return all three clones (pill, label, text) for this option
    return pill_clone, label_clone, text_clone


def format_all_mcq_options(
    options_data: list[dict],
) -> list[tuple[etree._Element, etree._Element, etree._Element]]:
    """Format all four MCQ options at once.

    Args:
        options_data: List of dicts with keys: pill_el, label_el, text_el
                     Must have exactly 4 options (A, B, C, D)

    Returns:
        List of tuples: [(pill_a, label_a, text_a), (pill_b, ...), ...]
    """
    # Validate we have exactly 4 options
    if len(options_data) != 4:
        raise ValueError(f"Expected 4 MCQ options, got {len(options_data)}")

    # Format each option and collect results
    formatted_options = []
    for option_idx, option_data in enumerate(options_data):
        # Extract the elements for this option
        pill_el = option_data["pill_el"]
        label_el = option_data["label_el"]
        text_el = option_data["text_el"]

        # Format this option (A, B, C, or D)
        pill_clone, label_clone, text_clone = format_mcq_option(
            option_idx,
            pill_el,
            label_el,
            text_el,
        )

        # Store the result
        formatted_options.append((pill_clone, label_clone, text_clone))

    # Return all formatted options
    return formatted_options
