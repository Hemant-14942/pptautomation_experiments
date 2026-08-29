"""Walks an input deck's slides and classifies each top-level shape into a
role ("heading", "title_heading", "option", "table", "picture", "body")
that app/core/template_converter/shape_emitter.py knows how to re-render
using the template's own shape vocabulary.
"""
from __future__ import annotations

import copy
from typing import Any

from lxml import etree
from pptx import Presentation

from app.constants.shape_geometry import (
    HEADING_CX,
    HEADING_CY,
    ICON_MAX_SIZE_FRACTION,
    ICON_ZONE_X_FRACTION,
    LABEL_PAIRING_TOLERANCE,
    OPTION_CX,
    OPTION_CY,
    TITLE_BANNER_WIDTH_FRACTION,
)
from app.constants.xml_namespaces import R
from app.core.design_spec import DesignSpec
from app.utils.xml_helpers import (
    local_name as _local,
    off_ext as _off_ext,
    prst_geom as _prst_geom,
    q as _q,
    text_of as _text_of,
)


def _find_paired_label(children: list, i: int, off, ext, claimed: set) -> etree._Element | None:
    if i + 1 < len(children):
        nxt = children[i + 1]
        if _local(nxt) == "sp" and id(nxt) not in claimed:
            claimed.add(id(nxt))
            return nxt
    if not off or not ext:
        return None
    for c in children:
        if id(c) in claimed or _local(c) != "sp":
            continue
        coff, cext = _off_ext(c, "p:spPr")
        if not coff or not cext:
            continue
        if abs(coff[0] - off[0]) < LABEL_PAIRING_TOLERANCE and abs(coff[1] - off[1]) < LABEL_PAIRING_TOLERANCE:
            claimed.add(id(c))
            return c
    return None


def collect_inputs(input_path: str, dspec: DesignSpec | None = None) -> list[dict[str, Any]]:
    """Per input slide: a list of classified shape items."""
    prs = Presentation(input_path)
    slide_width, slide_height = prs.slide_width, prs.slide_height
    out: list[dict[str, Any]] = []
    for idx, slide in enumerate(prs.slides):
        sptree = slide._element.find(_q("p:cSld") + "/" + _q("p:spTree"))
        if sptree is None:
            out.append({"index": idx, "items": []})
            continue

        children = [c for c in list(sptree) if _local(c) in {"sp", "pic", "grpSp", "graphicFrame"}]
        claimed: set = set()
        items: list[dict[str, Any]] = []

        for i, child in enumerate(children):
            if id(child) in claimed:
                continue
            tag = _local(child)

            if tag == "sp":
                geom = _prst_geom(child)
                off, ext = _off_ext(child, "p:spPr")

                if (
                    dspec is not None
                    and dspec.title_banner_el is not None
                    and geom == "roundRect"
                    and ext
                    and ext[0] >= slide_width * TITLE_BANNER_WIDTH_FRACTION
                ):
                    label = _find_paired_label(children, i, off, ext, claimed)
                    label_off, label_ext = _off_ext(label, "p:spPr") if label is not None else (off, ext)
                    # Drop this slide's own icon badge/pictures near the
                    # banner -- they're replaced wholesale by the
                    # template's own icon graphic, not restyled in place.
                    for c in children:
                        if id(c) in claimed or c is child:
                            continue
                        if _local(c) not in {"sp", "pic"}:
                            continue
                        c_off, c_ext = _off_ext(c, "p:spPr")
                        if not c_off or not c_ext:
                            continue
                        c_cx_center = c_off[0] + c_ext[0] / 2
                        if c_cx_center >= slide_width * ICON_ZONE_X_FRACTION:
                            continue
                        if c_ext[0] >= slide_width * ICON_MAX_SIZE_FRACTION or c_ext[1] >= slide_height * ICON_MAX_SIZE_FRACTION:
                            continue
                        if not (c_off[1] < off[1] + ext[1] and c_off[1] + c_ext[1] > off[1]):
                            continue
                        claimed.add(id(c))
                    items.append({
                        "kind": "title_heading",
                        "off": off, "ext": ext,
                        "label_text": _text_of(label) if label is not None else "",
                        "label_off": label_off or off, "label_ext": label_ext or ext,
                    })
                    continue

                if geom == "roundRect" and ext and HEADING_CX[0] <= ext[0] <= HEADING_CX[1] and HEADING_CY[0] <= ext[1] <= HEADING_CY[1]:
                    label = _find_paired_label(children, i, off, ext, claimed)
                    label_off, label_ext = _off_ext(label, "p:spPr") if label is not None else (off, ext)
                    items.append({
                        "kind": "heading",
                        "off": off, "ext": ext,
                        "label_text": _text_of(label) if label is not None else "Question",
                        "label_off": label_off or off, "label_ext": label_ext or ext,
                        "orig_pill_xml": copy.deepcopy(child),
                        "orig_label_xml": copy.deepcopy(label) if label is not None else None,
                    })
                    continue

                if geom == "ellipse" and ext and OPTION_CX[0] <= ext[0] <= OPTION_CX[1] and OPTION_CY[0] <= ext[1] <= OPTION_CY[1]:
                    label = _find_paired_label(children, i, off, ext, claimed)
                    label_text = _text_of(label) if label is not None else "?"
                    letter = (label_text.strip()[:1] or "?").upper()
                    label_off, label_ext = _off_ext(label, "p:spPr") if label is not None else (off, ext)
                    items.append({
                        "kind": "option", "grouped": False, "letter": letter,
                        "off": off, "ext": ext,
                        "label_text": label_text or letter,
                        "label_off": label_off or off, "label_ext": label_ext or ext,
                        "orig_pill_xml": copy.deepcopy(child),
                        "orig_label_xml": copy.deepcopy(label) if label is not None else None,
                    })
                    continue

                items.append({"kind": "body", "xml": copy.deepcopy(child)})

            elif tag == "grpSp":
                inner_sps = [c for c in child if _local(c) == "sp"]
                pill_el = next((c for c in inner_sps if _prst_geom(c) == "ellipse"), None)
                label_el = next((c for c in inner_sps if c is not pill_el and _text_of(c)), None)
                if pill_el is not None:
                    off, ext = _off_ext(child, "p:grpSpPr")
                    label_text = _text_of(label_el) if label_el is not None else "?"
                    letter = (label_text.strip()[:1] or "?").upper()
                    items.append({
                        "kind": "option", "grouped": True, "letter": letter,
                        "off": off, "ext": ext,
                        "label_text": label_text or letter,
                        "orig_xml": copy.deepcopy(child),
                    })
                else:
                    items.append({"kind": "body", "xml": copy.deepcopy(child)})

            elif tag == "graphicFrame":
                graphic = child.find(".//" + _q("a:graphicData"))
                uri = graphic.get("uri", "") if graphic is not None else ""
                if "table" in uri.lower():
                    items.append({"kind": "table", "xml": copy.deepcopy(child)})
                else:
                    items.append({"kind": "body", "xml": copy.deepcopy(child)})

            elif tag == "pic":
                off, ext = _off_ext(child, "p:spPr")
                blip = child.find(".//" + _q("a:blip"))
                rid = blip.get("{%s}embed" % R) if blip is not None else None
                image_bytes = None
                image_ext = None
                if rid:
                    try:
                        target_part = slide.part.rels[rid].target_part
                        image_bytes = target_part.blob
                        image_ext = target_part.partname.ext.lstrip(".")
                    except (KeyError, AttributeError):
                        pass
                items.append({
                    "kind": "picture", "xml": copy.deepcopy(child), "off": off, "ext": ext,
                    "image_bytes": image_bytes, "image_ext": image_ext,
                })

        out.append({"index": idx, "items": items})
    return out
