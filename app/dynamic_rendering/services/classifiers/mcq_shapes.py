"""Classify MCQ heading pill and option shapes on input slides."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import HEADING_CX, HEADING_CY, OPTION_CX, OPTION_CY
from app.dynamic_rendering.services.classifiers.heading_adjust import find_paired_label
from app.dynamic_rendering.utils.xml.helpers import off_ext, prst_geom, text_of


def classify_mcq_heading(
    child: etree._Element,
    children: list,
    i: int,
    off,
    ext,
    claimed: set,
) -> dict[str, Any] | None:
    geom = prst_geom(child)
    if not (
        geom == "roundRect"
        and ext
        and HEADING_CX[0] <= ext[0] <= HEADING_CX[1]
        and HEADING_CY[0] <= ext[1] <= HEADING_CY[1]
    ):
        return None

    label = find_paired_label(children, i, off, ext, claimed)
    label_off, label_ext = off_ext(label, "p:spPr") if label is not None else (off, ext)
    return {
        "kind": "heading",
        "off": off,
        "ext": ext,
        "label_text": text_of(label) if label is not None else "Question",
        "label_off": label_off or off,
        "label_ext": label_ext or ext,
        "orig_pill_xml": copy.deepcopy(child),
        "orig_label_xml": copy.deepcopy(label) if label is not None else None,
    }


def classify_standalone_option(
    child: etree._Element,
    children: list,
    i: int,
    off,
    ext,
    claimed: set,
) -> dict[str, Any] | None:
    geom = prst_geom(child)
    if not (
        geom == "ellipse"
        and ext
        and OPTION_CX[0] <= ext[0] <= OPTION_CX[1]
        and OPTION_CY[0] <= ext[1] <= OPTION_CY[1]
    ):
        return None

    label = find_paired_label(children, i, off, ext, claimed)
    label_text = text_of(label) if label is not None else "?"
    letter = (label_text.strip()[:1] or "?").upper()
    label_off, label_ext = off_ext(label, "p:spPr") if label is not None else (off, ext)
    return {
        "kind": "option",
        "grouped": False,
        "letter": letter,
        "off": off,
        "ext": ext,
        "label_text": label_text or letter,
        "label_off": label_off or off,
        "label_ext": label_ext or ext,
        "orig_pill_xml": copy.deepcopy(child),
        "orig_label_xml": copy.deepcopy(label) if label is not None else None,
    }


def classify_grouped_option(child: etree._Element) -> dict[str, Any] | None:
    from app.dynamic_rendering.utils.xml.helpers import local_name

    inner_sps = [c for c in child if local_name(c) == "sp"]
    pill_el = next((c for c in inner_sps if prst_geom(c) == "ellipse"), None)
    label_el = next((c for c in inner_sps if c is not pill_el and text_of(c)), None)
    if pill_el is None:
        return None

    off, ext = off_ext(child, "p:grpSpPr")
    label_text = text_of(label_el) if label_el is not None else "?"
    letter = (label_text.strip()[:1] or "?").upper()
    return {
        "kind": "option",
        "grouped": True,
        "letter": letter,
        "off": off,
        "ext": ext,
        "label_text": label_text or letter,
        "orig_xml": copy.deepcopy(child),
    }
