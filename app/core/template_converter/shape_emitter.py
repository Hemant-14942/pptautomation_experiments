"""Emits output-deck shapes for each classified input item (see
shape_collector.py), cloning the matching element out of the template's
DesignSpec and re-homing it (position, fill, text, colors, fonts, image
relationships) onto the current output slide.
"""
from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.constants.shape_geometry import (
    LOGO_DUPLICATE_POSITION_TOLERANCE,
    LOGO_DUPLICATE_SIZE_TOLERANCE,
    LOGO_RECLONE_TOLERANCE,
)
from app.constants.xml_namespaces import R
from app.core.design_spec import DesignSpec
from app.core.template_converter.xml_utils import (
    clone_and_place,
    enable_text_wrapping,
    place_group,
    rects_close,
    renumber_ids,
    set_all_run_colors,
    set_all_run_fonts,
    set_all_run_sizes,
    set_shape_fill,
    set_text,
    strip_blip_ext_lst,
    strip_run_overrides,
)
from app.utils.xml_helpers import local_name as _local, off_ext as _off_ext, prst_geom as _prst_geom, q as _q


def emit_heading(spTree: etree._Element, item: dict[str, Any], dspec: DesignSpec, id_state: dict[str, int]) -> None:
    emitted = False
    if dspec.heading_pill_el is not None:
        pill = clone_and_place(dspec.heading_pill_el, item["off"], item["ext"])
        set_shape_fill(pill, dspec.heading_fill)
        renumber_ids(pill, id_state)
        spTree.append(pill)
        emitted = True
    if dspec.heading_label_el is not None:
        label = clone_and_place(dspec.heading_label_el, item["label_off"], item["label_ext"])
        set_text(label, item["label_text"])
        set_all_run_colors(label, dspec.heading_text_color)
        if dspec.heading_font:
            set_all_run_fonts(label, dspec.heading_font)
        renumber_ids(label, id_state)
        spTree.append(label)
        emitted = True
    if not emitted:
        # Defensive fallback: the template had nothing we could clone for
        # this role -- keep the input's own pill/label rather than lose it.
        if item.get("orig_pill_xml") is not None:
            spTree.append(copy.deepcopy(item["orig_pill_xml"]))
        if item.get("orig_label_xml") is not None:
            spTree.append(copy.deepcopy(item["orig_label_xml"]))


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

    if _local(template_el) == "grpSp":
        clone = copy.deepcopy(template_el)
        place_group(clone, item["off"], item["ext"])
        inner_sps = [c for c in clone if _local(c) == "sp"]
        pill_el = next((c for c in inner_sps if _prst_geom(c) == "ellipse"), None)
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


def emit_body(spTree: etree._Element, item: dict[str, Any], dspec: DesignSpec) -> None:
    xml_el = copy.deepcopy(item["xml"])
    txBody = xml_el.find(_q("p:txBody"))
    if txBody is not None:
        strip_run_overrides(txBody)
        set_all_run_colors(xml_el, dspec.body_text_color)
        if dspec.body_font:
            set_all_run_fonts(xml_el, dspec.body_font)
    spTree.append(xml_el)


def _looks_like_logo_duplicate(item: dict[str, Any], dspec: DesignSpec) -> bool:
    if dspec.logo_el is None or dspec.logo_ext is None:
        return False
    ext = item.get("ext")
    if not ext:
        return False
    return rects_close(
        item.get("off") or (0, 0), ext, item.get("off") or (0, 0), dspec.logo_ext,
        tol=LOGO_DUPLICATE_POSITION_TOLERANCE,
    ) and abs(ext[0] - dspec.logo_ext[0]) < LOGO_DUPLICATE_SIZE_TOLERANCE and abs(ext[1] - dspec.logo_ext[1]) < LOGO_DUPLICATE_SIZE_TOLERANCE


def emit_picture(
    spTree: etree._Element,
    item: dict[str, Any],
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    out_parts: dict[str, bytes],
    pic_media_state: dict[str, int],
) -> None:
    if _looks_like_logo_duplicate(item, dspec):
        return  # the template's own logo will be cloned onto this slide instead

    clone = copy.deepcopy(item["xml"])
    blip = clone.find(".//" + _q("a:blip"))
    if blip is None:
        spTree.append(clone)  # nothing to rewire, e.g. no fill picture
        return
    strip_blip_ext_lst(blip)

    image_bytes = item.get("image_bytes")
    if image_bytes is None:
        # The input's own rId can't be reused as-is (it belonged to the
        # input archive's own rels, not the output's) and no source bytes
        # were resolved -- appending it anyway would leave a dangling
        # relationship the output can't be opened with. Drop it instead.
        print("[builder] warning: dropped a picture with no resolvable source image")
        return

    pic_media_state["next"] += 1
    ext = item.get("image_ext") or "png"
    partname = f"ppt/media/input_pic_{pic_media_state['next']}.{ext}"
    out_parts[partname] = image_bytes

    rid = f"rIdPic{id_state['next'] + 1}"
    blip.set("{%s}embed" % R, rid)
    renumber_ids(clone, id_state)
    spTree.append(clone)

    rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", "../media/" + partname.rsplit("/", 1)[-1])


def emit_title_heading(
    spTree: etree._Element,
    item: dict[str, Any],
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    title_icon_media_partname: str | None,
) -> None:
    """The topic-title banner heading: template's own banner shape + icon
    picture, cloned in like the logo, with the input's title text."""
    wrap_mode = item.get("wrap_mode", False)

    if dspec.title_banner_el is not None:
        banner = clone_and_place(dspec.title_banner_el, item["off"], item["ext"])
        set_shape_fill(banner, dspec.heading_fill)
        if dspec.title_label_el is None and item.get("label_text"):
            set_text(banner, item["label_text"])
            set_all_run_colors(banner, dspec.heading_text_color)
            if dspec.heading_font:
                set_all_run_fonts(banner, dspec.heading_font)
            if item.get("label_font_size_pt") is not None:
                set_all_run_sizes(banner, item["label_font_size_pt"])
            if wrap_mode:
                enable_text_wrapping(banner)
        renumber_ids(banner, id_state)
        spTree.append(banner)

    if dspec.title_label_el is not None:
        label = clone_and_place(dspec.title_label_el, item["label_off"], item["label_ext"])
        set_text(label, item["label_text"])
        set_all_run_colors(label, dspec.heading_text_color)
        if dspec.heading_font:
            set_all_run_fonts(label, dspec.heading_font)
        if item.get("label_font_size_pt") is not None:
            set_all_run_sizes(label, item["label_font_size_pt"])
        if wrap_mode:
            enable_text_wrapping(label)
        renumber_ids(label, id_state)
        spTree.append(label)

    # label_template = dspec.title_label_el if dspec.title_label_el is not None else dspec.heading_label_el
    # if label_template is not None:
    #     label = clone_and_place(label_template, item["label_off"], item["label_ext"])
    #     set_text(label, item["label_text"])
    #     set_all_run_colors(label, dspec.heading_text_color)
    #     if dspec.heading_font:
    #         set_all_run_fonts(label, dspec.heading_font)
    #     renumber_ids(label, id_state)
    #     spTree.append(label)

    if dspec.title_icon_el is not None:
        icon_off = item.get("icon_off") or dspec.title_icon_off
        icon_ext = item.get("icon_ext") or dspec.title_icon_ext
        if _local(dspec.title_icon_el) == "grpSp":
            clone = copy.deepcopy(dspec.title_icon_el)
            place_group(clone, icon_off, icon_ext)
        else:
            clone = clone_and_place(dspec.title_icon_el, icon_off, icon_ext)
        blip = clone.find(".//" + _q("a:blip"))
        if blip is not None and title_icon_media_partname is not None:
            strip_blip_ext_lst(blip)
            rid = f"rIdTitleIcon{id_state['next'] + 1}"
            blip.set("{%s}embed" % R, rid)
            rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
            rel_el.set("Id", rid)
            rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
            rel_el.set("Target", "../" + title_icon_media_partname.replace("ppt/", ""))
        elif blip is not None and title_icon_media_partname is None and _local(dspec.title_icon_el) != "grpSp":
            clone = None
        if clone is not None:
            renumber_ids(clone, id_state)
            spTree.append(clone)


def emit_question_icon(
    spTree: etree._Element,
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    question_icon_media_partname: str | None,
) -> None:
    """MCQ '?' badge — only for slides that have a Question pill."""
    if dspec.question_icon_el is None or question_icon_media_partname is None:
        return
    clone = clone_and_place(dspec.question_icon_el, dspec.question_icon_off, dspec.question_icon_ext)
    blip = clone.find(".//" + _q("a:blip"))
    if blip is None:
        return
    strip_blip_ext_lst(blip)
    rid = f"rIdQuestionIcon{id_state['next'] + 1}"
    blip.set("{%s}embed" % R, rid)
    renumber_ids(clone, id_state)
    spTree.append(clone)
    rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", "../" + question_icon_media_partname.replace("ppt/", ""))


def emit_logo(
    spTree: etree._Element,
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    logo_media_partname: str | None,
) -> None:
    if dspec.logo_el is None or logo_media_partname is None:
        return
    for existing in spTree.iter(_q("p:pic")):
        off, ext = _off_ext(existing, "p:spPr")
        if rects_close(off, ext, dspec.logo_off, dspec.logo_ext, tol=LOGO_RECLONE_TOLERANCE):
            return  # this slide's cloned template background already carries it
    clone = clone_and_place(dspec.logo_el, dspec.logo_off, dspec.logo_ext)
    blip = clone.find(".//" + _q("a:blip"))
    if blip is None:
        return
    strip_blip_ext_lst(blip)
    rid = f"rIdLogo{id_state['next'] + 1}"
    blip.set("{%s}embed" % R, rid)
    renumber_ids(clone, id_state)
    spTree.append(clone)
    rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", "../" + logo_media_partname.replace("ppt/", ""))
