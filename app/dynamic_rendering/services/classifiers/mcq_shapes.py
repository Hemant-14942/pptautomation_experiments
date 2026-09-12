"""Classify MCQ heading pill and option shapes on input slides."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import HEADING_CX, HEADING_CY
from app.dynamic_rendering.services.classifiers.heading_adjust import find_paired_label
from app.dynamic_rendering.services.classifiers.option_label import (
    find_input_option_ellipse_el,
    find_input_option_label_el,
    is_input_option_ellipse_el,
    is_input_option_group_el,
    parse_input_option_label,
)
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, prst_geom, text_of


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
    if not is_input_option_ellipse_el(child):
        return None

    label = find_paired_label(children, i, off, ext, claimed)
    label_text = text_of(label) if label is not None else ""
    letter = parse_input_option_label(label_text)
    if letter is None:
        return None
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
    if not is_input_option_group_el(child):
        return None

    inner_sps = [c for c in child if local_name(c) == "sp"]
    pill_el = find_input_option_ellipse_el(inner_sps)
    label_el = find_input_option_label_el(inner_sps, pill_el)
    if pill_el is None or label_el is None:
        return None

    off, ext = off_ext(child, "p:grpSpPr")
    label_text = (text_of(label_el) or "").strip()
    letter = parse_input_option_label(label_text) or "?"
    return {
        "kind": "option",
        "grouped": True,
        "letter": letter,
        "off": off,
        "ext": ext,
        "label_text": label_text or letter,
        "orig_xml": copy.deepcopy(child),
    }
