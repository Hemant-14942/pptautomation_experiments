"""Locate title banner, icon, and label shapes on input title slides."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.constants.shape_geometry import (
    ICON_MAX_SIZE_FRACTION,
    ICON_ZONE_X_FRACTION,
    TITLE_BANNER_WIDTH_FRACTION,
)
from app.dynamic_rendering.services.classifiers.heading_adjust import find_paired_label
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, prst_geom, text_of


def find_title_heading_shapes(slide: Slide, slide_width: int) -> dict | None:
    sptree = slide.shapes._spTree
    children = [c for c in list(sptree) if local_name(c) in {"sp", "pic"}]
    claimed: set[int] = set()

    banner_el = None
    banner_off = None
    banner_ext = None
    label_el = None
    icon_el = None

    for i, child in enumerate(children):
        if prst_geom(child) != "roundRect":
            continue
        off, ext = off_ext(child, "p:spPr")
        if not off or not ext or ext[0] < slide_width * TITLE_BANNER_WIDTH_FRACTION:
            continue
        banner_el = child
        banner_off, banner_ext = off, ext
        label_el = find_paired_label(children, i, off, ext, claimed)
        break

    if banner_el is None or banner_off is None or banner_ext is None:
        return None

    banner_bottom = banner_off[1] + banner_ext[1]
    for child in children:
        if local_name(child) != "pic" or id(child) in claimed:
            continue
        off, ext = off_ext(child, "p:spPr")
        if not off or not ext:
            continue
        center_x = off[0] + ext[0] / 2
        if center_x >= slide_width * ICON_ZONE_X_FRACTION:
            continue
        if ext[0] >= slide_width * ICON_MAX_SIZE_FRACTION:
            continue
        if not (off[1] < banner_bottom and off[1] + ext[1] > banner_off[1]):
            continue
        icon_el = child
        claimed.add(id(child))
        break

    if label_el is None:
        for child in children:
            if id(child) in claimed or local_name(child) != "sp":
                continue
            if not child.findall(".//{*}t"):
                continue
            text = (text_of(child) or "").strip()
            if not text:
                continue
            off, ext = off_ext(child, "p:spPr")
            if not off or not ext:
                continue
            if off[1] >= banner_off[1] and off[1] < banner_bottom:
                label_el = child
                claimed.add(id(child))
                break

    return {
        "banner_el": banner_el,
        "label_el": label_el,
        "icon_el": icon_el,
    }
