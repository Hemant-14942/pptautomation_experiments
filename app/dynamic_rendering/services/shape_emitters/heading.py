"""Emit MCQ heading pill and title banner shapes."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.template_design import FIXED_HEADING_FONT_PT, QUESTION_LABEL_FONT_PT
from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import local_name, q
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    enable_text_wrapping,
    place_group,
    renumber_ids,
    set_all_run_colors,
    set_all_run_fonts,
    set_all_run_sizes,
    set_shape_fill,
    set_text,
    strip_blip_ext_lst,
)


def emit_heading(spTree: etree._Element, item: dict[str, Any], dspec: DesignSpec, id_state: dict[str, int]) -> None:
    emitted = False
    if dspec.question_pill_el is not None:
        pill = clone_and_place(dspec.question_pill_el, item["off"], item["ext"])
        set_shape_fill(pill, dspec.question_pill_fill)
        renumber_ids(pill, id_state)
        spTree.append(pill)
        emitted = True
    if dspec.question_pill_label_el is not None:
        label = clone_and_place(dspec.question_pill_label_el, item["label_off"], item["label_ext"])
        set_text(label, item["label_text"])
        set_all_run_colors(label, dspec.question_pill_text_color)
        if dspec.question_pill_font:
            set_all_run_fonts(label, dspec.question_pill_font)
        set_all_run_sizes(label, QUESTION_LABEL_FONT_PT)
        renumber_ids(label, id_state)
        spTree.append(label)
        emitted = True
    if not emitted:
        if item.get("orig_pill_xml") is not None:
            spTree.append(copy.deepcopy(item["orig_pill_xml"]))
        if item.get("orig_label_xml") is not None:
            spTree.append(copy.deepcopy(item["orig_label_xml"]))


def emit_title_heading(
    spTree: etree._Element,
    item: dict[str, Any],
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    title_icon_media_partname: str | None,
) -> None:
    """Topic-title banner: template banner + icon, with input title text."""
    wrap_mode = item.get("wrap_mode", False)

    if dspec.title_banner_el is not None:
        banner = clone_and_place(dspec.title_banner_el, item["off"], item["ext"])
        set_shape_fill(banner, dspec.question_pill_fill)
        if dspec.title_label_el is None and item.get("label_text"):
            set_text(banner, item["label_text"])
            set_all_run_colors(banner, dspec.question_pill_text_color)
            if dspec.question_pill_font:
                set_all_run_fonts(banner, dspec.question_pill_font)
            if item.get("label_font_size_pt") is not None:
                set_all_run_sizes(banner, item["label_font_size_pt"])
            else:
                set_all_run_sizes(banner, FIXED_HEADING_FONT_PT)
            if wrap_mode:
                enable_text_wrapping(banner)
        renumber_ids(banner, id_state)
        spTree.append(banner)

    if dspec.title_label_el is not None:
        label = clone_and_place(dspec.title_label_el, item["label_off"], item["label_ext"])
        set_text(label, item["label_text"])
        set_all_run_colors(label, dspec.question_pill_text_color)
        if dspec.question_pill_font:
            set_all_run_fonts(label, dspec.question_pill_font)
        if item.get("label_font_size_pt") is not None:
            set_all_run_sizes(label, item["label_font_size_pt"])
        else:
            set_all_run_sizes(label, FIXED_HEADING_FONT_PT)
        if wrap_mode:
            enable_text_wrapping(label)
        renumber_ids(label, id_state)
        spTree.append(label)

    if dspec.title_icon_el is not None:
        icon_off = item.get("icon_off") or dspec.title_icon_off
        icon_ext = item.get("icon_ext") or dspec.title_icon_ext
        if local_name(dspec.title_icon_el) == "grpSp":
            clone = copy.deepcopy(dspec.title_icon_el)
            place_group(clone, icon_off, icon_ext)
        else:
            clone = clone_and_place(dspec.title_icon_el, icon_off, icon_ext)
        blip = clone.find(".//" + q("a:blip"))
        if blip is not None and title_icon_media_partname is not None:
            strip_blip_ext_lst(blip)
            rid = f"rIdTitleIcon{id_state['next'] + 1}"
            blip.set("{%s}embed" % R, rid)
            rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
            rel_el.set("Id", rid)
            rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
            rel_el.set("Target", "../" + title_icon_media_partname.replace("ppt/", ""))
        elif blip is not None and title_icon_media_partname is None and local_name(dspec.title_icon_el) != "grpSp":
            clone = None
        if clone is not None:
            renumber_ids(clone, id_state)
            spTree.append(clone)
