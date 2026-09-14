"""Text box layout helpers for fit-layout formatters."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    BODY_LONG_LIST_PARAGRAPH_THRESHOLD,
)
from app.dynamic_rendering.utils.xml.helpers import q, text_of
from app.dynamic_rendering.utils.xml.shape_mutators import enable_shrink_to_fit


def _tx_body_and_body_pr(el: etree._Element) -> tuple[etree._Element | None, etree._Element | None]:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return None, None
    bodyPr = txBody.find(q("a:bodyPr"))
    if bodyPr is None:
        bodyPr = etree.SubElement(txBody, q("a:bodyPr"))
    return txBody, bodyPr


def enable_body_text_wrapping(el: etree._Element) -> None:
    """Wrap body text and left-align paragraphs without forcing vertical anchor."""
    txBody, bodyPr = _tx_body_and_body_pr(el)
    if txBody is None or bodyPr is None:
        return
    bodyPr.set("wrap", "square")
    bodyPr.set("anchorCtr", "0")
    bodyPr.set("rtlCol", "0")
    for p in txBody.findall(q("a:p")):
        pPr = p.find(q("a:pPr"))
        if pPr is None:
            pPr = etree.Element(q("a:pPr"))
            p.insert(0, pPr)
        pPr.set("algn", "l")


def set_vertical_center_anchor(el: etree._Element) -> None:
    _, bodyPr = _tx_body_and_body_pr(el)
    if bodyPr is None:
        return
    bodyPr.set("anchor", "ctr")


def set_vertical_top_anchor(el: etree._Element) -> None:
    _, bodyPr = _tx_body_and_body_pr(el)
    if bodyPr is None:
        return
    bodyPr.set("anchor", "t")


def count_nonempty_paragraphs(el: etree._Element) -> int:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        txBody = el.find(q("a:txBody"))
    if txBody is None:
        return 0
    return sum(1 for p in txBody.findall(q("a:p")) if text_of(p).strip())


def configure_body_text_layout(el: etree._Element) -> None:
    """Wrap + shrink-to-fit; top-align only when paragraph count exceeds threshold."""
    enable_body_text_wrapping(el)
    if count_nonempty_paragraphs(el) > BODY_LONG_LIST_PARAGRAPH_THRESHOLD:
        set_vertical_top_anchor(el)
    else:
        set_vertical_center_anchor(el)
    enable_shrink_to_fit(el)
