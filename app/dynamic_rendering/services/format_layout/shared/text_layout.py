"""Text box layout helpers for fit-layout formatters."""

from lxml import etree

from app.dynamic_rendering.utils.xml.helpers import q


def set_vertical_center_anchor(el: etree._Element) -> None:
    txBody = el.find(q("p:txBody"))
    if txBody is None:
        return
    bodyPr = txBody.find(q("a:bodyPr"))
    if bodyPr is None:
        return
    bodyPr.set("anchor", "ctr")
