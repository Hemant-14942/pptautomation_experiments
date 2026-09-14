"""Fixed title heading geometry from standard-red.pptx (banner + icon + label)."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.utils.xml.shape_mutators import clone_and_place, enable_text_wrapping
from app.dynamic_rendering.constants.shape_geometry import DEFENCE_BANNER_HEIGHT_EMU

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




def box_off_ext( box: dict[str, int],dspec=None,) -> tuple[tuple[int, int], tuple[int, int]]:
    y = box["y"]
    if dspec is not None and dspec.has_top_banner():
        y = y + DEFENCE_BANNER_HEIGHT_EMU
    return (box["x"], y), (box["width"], box["height"])

def fixed_title_heading_geometry(dspec=None) -> dict[str, tuple[int, int]]:
    banner_off, banner_ext = box_off_ext(TITLE_BANNER, dspec)
    label_off, label_ext = box_off_ext(TITLE_LABEL, dspec)
    icon_off, icon_ext = box_off_ext(TITLE_ICON, dspec)
    return {
        "banner_off": banner_off,
        "banner_ext": banner_ext,
        "label_off": label_off,
        "label_ext": label_ext,
        "icon_off": icon_off,
        "icon_ext": icon_ext,
    }


def format_title_banner(el: etree._Element,dspec=None) -> etree._Element:
    off, ext = box_off_ext(TITLE_BANNER, dspec)
    return clone_and_place(el, off, ext)


def format_title_icon(el: etree._Element,dspec=None) -> etree._Element:
    off, ext = box_off_ext(TITLE_ICON, dspec)
    return clone_and_place(el, off, ext)


def format_title_label(el: etree._Element,dspec=None) -> etree._Element:
    off, ext = box_off_ext(TITLE_LABEL, dspec)
    clone = clone_and_place(el, off, ext)
    enable_text_wrapping(clone)
    return clone
