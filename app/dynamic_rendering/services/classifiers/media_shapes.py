"""Classify title banner shapes and table/picture shapes."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import (
    ICON_MAX_SIZE_FRACTION,
    ICON_ZONE_X_FRACTION,
    TITLE_BANNER_WIDTH_FRACTION,
)
from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.classifiers.heading_adjust import find_paired_label
from app.dynamic_rendering.services.format_layout.shared.title_heading_layout import fixed_title_heading_geometry
from app.dynamic_rendering.services.text.title_heading_fit import fit_title_heading
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, prst_geom, q, text_of


def classify_title_banner(
    child: etree._Element,
    children: list,
    i: int,
    off,
    ext,
    claimed: set,
    dspec: DesignSpec,
    slide_width: int,
    slide_height: int,
) -> dict[str, Any] | None:
    geom = prst_geom(child)
    if not (
        dspec.title_banner_el is not None
        and geom == "roundRect"
        and ext
        and ext[0] >= slide_width * TITLE_BANNER_WIDTH_FRACTION
    ):
        return None

    label = find_paired_label(children, i, off, ext, claimed)
    label_off, label_ext = off_ext(label, "p:spPr") if label is not None else (off, ext)

    for c in children:
        if id(c) in claimed or c is child:
            continue
        if local_name(c) not in {"sp", "pic"}:
            continue
        c_off, c_ext = off_ext(c, "p:spPr")
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

    label_text_val = text_of(label) if label is not None else ""
    geo = fixed_title_heading_geometry()
    banner_off = geo["banner_off"]
    banner_ext = geo["banner_ext"]
    label_off = geo["label_off"]
    label_ext = geo["label_ext"]
    fit = fit_title_heading(
        text=label_text_val,
        banner_off=banner_off,
        banner_ext=banner_ext,
        label_off=label_off,
        label_ext=label_ext,
        baseline_font_size_pt=dspec.title_heading_font_size_pt,
        slide_width=slide_width,
    )
    return {
        "kind": "title_heading",
        "off": banner_off,
        "ext": fit.banner_ext,
        "label_text": label_text_val,
        "label_off": label_off,
        "label_ext": fit.label_ext,
        "label_font_size_pt": fit.label_font_size_pt,
        "wrap_mode": fit.wrap_mode,
        "icon_off": geo["icon_off"],
        "icon_ext": geo["icon_ext"],
        "_orig_off": banner_off,
        "_orig_ext": banner_ext,
        "_orig_label_off": label_off,
        "_orig_label_ext": label_ext,
    }


def classify_graphic_frame(child: etree._Element) -> dict[str, Any]:
    graphic = child.find(".//" + q("a:graphicData"))
    uri = graphic.get("uri", "") if graphic is not None else ""
    if "table" in uri.lower():
        return {"kind": "table", "xml": copy.deepcopy(child)}
    return {"kind": "body", "xml": copy.deepcopy(child)}


def classify_picture(child: etree._Element, slide) -> dict[str, Any]:
    off, ext = off_ext(child, "p:spPr")
    blip = child.find(".//" + q("a:blip"))
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
    return {
        "kind": "picture",
        "xml": copy.deepcopy(child),
        "off": off,
        "ext": ext,
        "image_bytes": image_bytes,
        "image_ext": image_ext,
    }
