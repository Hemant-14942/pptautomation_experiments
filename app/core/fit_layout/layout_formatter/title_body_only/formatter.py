"""Format a title_body_only slide: position body text in full-width-ish box,
center it vertically, enable wrapping."""

from lxml import etree

from app.core.template_converter.xml_utils import clone_and_place, enable_text_wrapping

from .constants import BODY_TEXTBOX


def _q(local_name: str) -> str:
    """Namespace-qualified tag name (DrawingML/PresentationML)."""
    ns = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    }
    prefix, name = local_name.split(":", 1) if ":" in local_name else ("a", local_name)
    return f"{{{ns.get(prefix, ns['a'])}}}{name}"


def set_vertical_center_anchor(el: etree._Element) -> None:
    """Set text to center vertically within the textbox.

    When text (2 lines or 5 lines) is inside this box, PowerPoint will
    center it top-to-bottom with equal padding above/below."""
    txBody = el.find(_q("p:txBody"))
    if txBody is None:
        return
    bodyPr = txBody.find(_q("a:bodyPr"))
    if bodyPr is None:
        return
    bodyPr.set("anchor", "ctr")


def format_body_only(body_shape_el: etree._Element) -> etree._Element:
    """Clone the input slide's body text into BODY_TEXTBOX, centered vertically.

    Args:
        body_shape_el: the body text shape element from the input slide

    Returns:
        cloned shape element, positioned in the fixed box, vertically centered,
        with wrap mode enabled
    """
    off = (BODY_TEXTBOX["x"], BODY_TEXTBOX["y"])
    ext = (BODY_TEXTBOX["width"], BODY_TEXTBOX["height"])
    clone = clone_and_place(body_shape_el, off, ext)
    enable_text_wrapping(clone)
    set_vertical_center_anchor(clone)
    return clone
