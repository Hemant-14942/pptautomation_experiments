"""Fixed title heading geometry from standard-red.pptx (banner + icon + label)."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.utils.xml.shape_mutators import clone_and_place, enable_text_wrapping

# Extracted from standard-red title design slide grpSp.
TITLE_BANNER = {
    "x": 1_780_335,
    "y": 843_803,
    "width": 13_675_975,
    "height": 2_748_660,
}

TITLE_ICON = {
    "x": 621_103,
    "y": -453_505,
    "width": 4_430_993,
    "height": 5_319_205,
}

TITLE_LABEL = {
    "x": 5_345_559,
    "y": 1_525_636,
    "width": 10_405_718,
    "height": 1_323_399,
}


def box_off_ext(box: dict[str, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    return (box["x"], box["y"]), (box["width"], box["height"])


def fixed_title_heading_geometry() -> dict[str, tuple[int, int]]:
    banner_off, banner_ext = box_off_ext(TITLE_BANNER)
    label_off, label_ext = box_off_ext(TITLE_LABEL)
    icon_off, icon_ext = box_off_ext(TITLE_ICON)
    return {
        "banner_off": banner_off,
        "banner_ext": banner_ext,
        "label_off": label_off,
        "label_ext": label_ext,
        "icon_off": icon_off,
        "icon_ext": icon_ext,
    }


def format_title_banner(el: etree._Element) -> etree._Element:
    off, ext = box_off_ext(TITLE_BANNER)
    return clone_and_place(el, off, ext)


def format_title_icon(el: etree._Element) -> etree._Element:
    off, ext = box_off_ext(TITLE_ICON)
    return clone_and_place(el, off, ext)


def format_title_label(el: etree._Element) -> etree._Element:
    off, ext = box_off_ext(TITLE_LABEL)
    clone = clone_and_place(el, off, ext)
    enable_text_wrapping(clone)
    return clone
