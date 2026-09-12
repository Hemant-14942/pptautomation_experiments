"""Detect MCQ option pills on blue input slides (ellipse standalone or grpSp)."""

from __future__ import annotations

from typing import Any

from pptx.slide import Slide

from app.dynamic_rendering.services.classifiers.heading_adjust import find_paired_label
from app.dynamic_rendering.services.classifiers.option_label import (
    find_input_option_ellipse_el,
    find_input_option_label_el,
    is_input_option_ellipse_el,
    is_input_option_group_el,
    parse_input_option_label,
)
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, prst_geom, text_of


def _top_emu(elem) -> int:
    off, _ = off_ext(elem, "p:grpSpPr" if local_name(elem) == "grpSp" else "p:spPr")
    return int(off[1]) if off else 0


def collect_input_mcq_options(slide: Slide) -> list[dict[str, Any]]:
    """Return input options sorted top-to-bottom: pill_el, label_el, letter."""
    sptree = slide.shapes._spTree
    children = [c for c in list(sptree) if local_name(c) in {"sp", "grpSp"}]
    claimed: set[int] = set()
    options: list[dict[str, Any]] = []

    for i, child in enumerate(children):
        if id(child) in claimed:
            continue
        tag = local_name(child)

        if tag == "grpSp":
            if not is_input_option_group_el(child):
                continue
            inner_sps = [c for c in child if local_name(c) == "sp"]
            pill_el = find_input_option_ellipse_el(inner_sps)
            label_el = find_input_option_label_el(inner_sps, pill_el)
            letter = parse_input_option_label(text_of(label_el) or "") if label_el is not None else None
            if letter is None:
                continue
            options.append(
                {
                    "pill_el": child,
                    "label_el": label_el,
                    "letter": letter,
                    "top": _top_emu(child),
                    "grouped": True,
                }
            )
            continue

        if not is_input_option_ellipse_el(child):
            continue

        off, ext = off_ext(child, "p:spPr")
        label_el = find_paired_label(children, i, off, ext, claimed)
        letter = parse_input_option_label(text_of(label_el) or "") if label_el is not None else None
        if letter is None:
            continue
        options.append(
            {
                "pill_el": child,
                "label_el": label_el,
                "letter": letter,
                "top": _top_emu(child),
                "grouped": False,
            }
        )

    options.sort(key=lambda item: item["top"])
    return options


def count_input_mcq_options(slide: Slide) -> int:
    return len(collect_input_mcq_options(slide))
