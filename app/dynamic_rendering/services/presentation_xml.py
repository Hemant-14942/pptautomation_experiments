"""Rewrite ppt/presentation.xml for the output slide list."""

from __future__ import annotations

import copy

from lxml import etree

from app.dynamic_rendering.constants.presentation_defaults import (
    DEFAULT_NOTES_HEIGHT,
    DEFAULT_NOTES_WIDTH,
    DEFAULT_SLIDE_HEIGHT,
    DEFAULT_SLIDE_WIDTH,
    FIRST_SLIDE_ID,
)
from app.dynamic_rendering.utils.xml.helpers import q


def extract_int_attr(xml_blob: bytes, tag: str, attr: str, default: int) -> int:
    if not xml_blob:
        return default
    root = etree.fromstring(xml_blob)
    el = root.find(q(tag))
    if el is None:
        return default
    try:
        return int(el.get(attr, default))
    except (ValueError, TypeError):
        return default


def extract_notes_size(xml_blob: bytes) -> tuple[int, int] | None:
    if not xml_blob:
        return None
    root = etree.fromstring(xml_blob)
    el = root.find(q("p:notesSz"))
    if el is None:
        return None
    try:
        return (int(el.get("cx", DEFAULT_NOTES_WIDTH)), int(el.get("cy", DEFAULT_NOTES_HEIGHT)))
    except (ValueError, TypeError):
        return None


def extract_default_text_style(xml_blob: bytes) -> etree._Element | None:
    if not xml_blob:
        return None
    root = etree.fromstring(xml_blob)
    el = root.find(q("p:defaultTextStyle"))
    return copy.deepcopy(el) if el is not None else None


def build_presentation_xml(
    num_slides: int,
    start_id: int = FIRST_SLIDE_ID,
    slide_width: int = DEFAULT_SLIDE_WIDTH,
    slide_height: int = DEFAULT_SLIDE_HEIGHT,
    notes_size: tuple[int, int] | None = None,
    default_text_style: etree._Element | None = None,
    base_pres_xml: bytes | None = None,
) -> etree._Element:
    """Reuse template presentation.xml wrapper; rewrite p:sldIdLst only."""
    if base_pres_xml:
        pres_xml = etree.fromstring(base_pres_xml)
    else:
        pres_xml = etree.fromstring(
            b"""<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                   xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                   xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <p:sldMasterIdLst>
        <p:sldMasterId id="2147483648" r:id="rId1"/>
      </p:sldMasterIdLst>
      <p:sldIdLst>
      </p:sldIdLst>
    </p:presentation>"""
        )

    sldIdLst = pres_xml.find(q("p:sldIdLst"))
    if sldIdLst is None:
        sldIdLst = etree.SubElement(pres_xml, q("p:sldIdLst"))
    for child in list(sldIdLst):
        sldIdLst.remove(child)
    for i in range(num_slides):
        sldId = etree.SubElement(sldIdLst, q("p:sldId"))
        sldId.set("id", str(start_id + i))
        sldId.set(q("r:id"), f"rId{i+100}")

    sldSz = pres_xml.find(q("p:sldSz"))
    if sldSz is None:
        sldSz = etree.SubElement(pres_xml, q("p:sldSz"))
    sldSz.set("cx", str(slide_width))
    sldSz.set("cy", str(slide_height))

    notesSz = pres_xml.find(q("p:notesSz"))
    if notesSz is None:
        notesSz = etree.SubElement(pres_xml, q("p:notesSz"))
    notesSz.set("cx", str(notes_size[0]) if notes_size else str(DEFAULT_NOTES_WIDTH))
    notesSz.set("cy", str(notes_size[1]) if notes_size else str(DEFAULT_NOTES_HEIGHT))
    return pres_xml
