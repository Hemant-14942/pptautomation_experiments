"""Emit MCQ option pill shapes."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import local_name, prst_geom
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    place_group,
    renumber_ids,
    set_all_run_colors,
    set_all_run_fonts,
    set_shape_fill,
    set_text,
)


def emit_option(spTree: etree._Element, item: dict[str, Any], dspec: DesignSpec, id_state: dict[str, int]) -> None:
    letter = item["letter"]
    color = dspec.option_color_for(letter)
    template_el = dspec.option_pill_group_el if item["grouped"] else dspec.option_pill_standalone_el
    if template_el is None:
        template_el = dspec.option_pill_standalone_el or dspec.option_pill_group_el

    if template_el is None:
        if item.get("orig_xml") is not None:
            spTree.append(copy.deepcopy(item["orig_xml"]))
        elif item.get("orig_pill_xml") is not None:
            spTree.append(copy.deepcopy(item["orig_pill_xml"]))
            if item.get("orig_label_xml") is not None:
                spTree.append(copy.deepcopy(item["orig_label_xml"]))
        return

    if local_name(template_el) == "grpSp":
        clone = copy.deepcopy(template_el)
        place_group(clone, item["off"], item["ext"])
        inner_sps = [c for c in clone if local_name(c) == "sp"]
        pill_el = next((c for c in inner_sps if prst_geom(c) == "ellipse"), None)
        label_el = next((c for c in inner_sps if c is not pill_el), None)
        if pill_el is not None:
            set_shape_fill(pill_el, color)
        if label_el is not None:
            set_text(label_el, item["label_text"])
            set_all_run_colors(label_el, dspec.option_text_color)
            if dspec.option_font:
                set_all_run_fonts(label_el, dspec.option_font)
        renumber_ids(clone, id_state)
        spTree.append(clone)
    else:
        pill = clone_and_place(template_el, item["off"], item["ext"])
        set_shape_fill(pill, color)
        renumber_ids(pill, id_state)
        spTree.append(pill)
        label_template = dspec.option_label_standalone_el
        if label_template is not None:
            label_off = item.get("label_off") or item["off"]
            label_ext = item.get("label_ext") or item["ext"]
            label = clone_and_place(label_template, label_off, label_ext)
            set_text(label, item["label_text"])
            set_all_run_colors(label, dspec.option_text_color)
            if dspec.option_font:
                set_all_run_fonts(label, dspec.option_font)
            renumber_ids(label, id_state)
            spTree.append(label)
