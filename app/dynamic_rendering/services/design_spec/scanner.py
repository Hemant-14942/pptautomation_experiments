"""
Heuristic scan of template .pptx zip for design tokens and cloneable shapes.

Finds: question pill, option pills, title banner, table colors.
"""

from __future__ import annotations

import copy
import os
import re
import zipfile
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.design_tokens_defaults import (
    DEFAULT_ACCENT,
    DEFAULT_QUESTION_PILL_FILL,
    DEFAULT_QUESTION_PILL_TEXT_COLOR,
    DEFAULT_OPTION_TEXT_COLOR,
    DEFAULT_TABLE_BODY_TEXT_COLOR,
    DEFAULT_TABLE_BORDER_COLOR,
    DEFAULT_TABLE_HEADER_FILL,
    DEFAULT_TABLE_HEADER_TEXT_COLOR,
)
from app.dynamic_rendering.constants.template_design import (
    MCQ_DESIGN_SLIDE_INDEX,
    TITLE_DESIGN_SLIDE_INDEX,
    resolve_slide_index,
)
from app.dynamic_rendering.constants.presentation_defaults import (
    DEFAULT_SLIDE_HEIGHT,
    DEFAULT_SLIDE_WIDTH,
)
from app.dynamic_rendering.constants.shape_geometry import (
    HEADING_CX,
    HEADING_CY,
)
from app.dynamic_rendering.services.classifiers.option_label import (
    build_template_option_labels,
    find_option_label_el,
    find_option_pill_el,
    option_labels_from_template_samples,
    parse_option_label,
)
from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.utils.xml.helpers import (
    in_range,
    local_name,
    off_ext,
    prst_geom,
    q,
    representative_rpr,
    text_of,
)

_SCHEME_ALIAS = {"tx1": "dk1", "bg1": "lt1", "tx2": "dk2", "bg2": "lt2"}
_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")

_TYPE_HEADING_RE = re.compile(r"type\s+heading\s+here", re.I)
_QUESTION_LABEL_RE = re.compile(r"^question$", re.I)
_DESIGN_NOTE_RE = re.compile(r"design purpose|PS\s*-", re.I)


def _design_slide_names(slide_names: list[str]) -> list[str]:
    """Only scan MCQ + title template slides (see constants/template_design.py)."""
    if not slide_names:
        return []
    count = len(slide_names)
    indices = sorted({
        resolve_slide_index(MCQ_DESIGN_SLIDE_INDEX, count),
        resolve_slide_index(TITLE_DESIGN_SLIDE_INDEX, count),
    })
    return [slide_names[i] for i in indices]


def _resolve_color(container: etree._Element | None, theme_colors: dict[str, str]) -> str | None:
    if container is None:
        return None
    srgb = container.find(q("a:srgbClr"))
    if srgb is not None:
        v = srgb.get("val", "")
        return v.upper() if _HEX_RE.match(v) else None
    scheme = container.find(q("a:schemeClr"))
    if scheme is not None:
        role = scheme.get("val", "")
        role = _SCHEME_ALIAS.get(role, role)
        v = theme_colors.get(role)
        if not v:
            return None
        return v.upper() if _HEX_RE.match(v) else None
    return None


def _fill_hex_of(sp: etree._Element, theme_colors: dict[str, str]) -> str | None:
    spPr = sp.find(q("p:spPr"))
    if spPr is None:
        return None
    solid = _resolve_color(spPr.find(q("a:solidFill")), theme_colors)
    if solid:
        return solid
    grad = spPr.find(q("a:gradFill"))
    if grad is None:
        return None
    for gs in grad.findall(".//" + q("a:gs")):
        hex_val = _resolve_color(gs, theme_colors)
        if hex_val:
            return hex_val
    return None


def _first_run_color(container: etree._Element, theme_colors: dict[str, str]) -> str | None:
    rPr = representative_rpr(container)
    if rPr is None:
        return None
    return _resolve_color(rPr.find(q("a:solidFill")), theme_colors)


def _parse_normal_text_color_from_last_slide(zf: zipfile.ZipFile) -> str | None:
    names = sorted(
        (n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )
    if not names:
        return None
    root = etree.fromstring(zf.read(names[-1]))
    blob = " ".join(text_of(el) for el in root.iter() if local_name(el) in {"sp", "grpSp"})
    if "for normal text" not in blob.lower():
        return None
    m = re.search(r"For Normal Text.{0,120}?Font Color\s*:\s*#([0-9A-Fa-f]{6})", blob, re.I | re.S)
    if not m:
        m = re.search(r"Font Color\s*:\s*#([0-9A-Fa-f]{6}).{0,80}?For Normal Text", blob, re.I | re.S)
    if m:
        return m.group(1).upper()
    return None


def _extract_slide_size(zf: zipfile.ZipFile) -> tuple[int, int]:
    if "ppt/presentation.xml" not in zf.namelist():
        return DEFAULT_SLIDE_WIDTH, DEFAULT_SLIDE_HEIGHT
    root = etree.fromstring(zf.read("ppt/presentation.xml"))
    sldSz = root.find(q("p:sldSz"))
    if sldSz is None:
        return DEFAULT_SLIDE_WIDTH, DEFAULT_SLIDE_HEIGHT
    try:
        return int(sldSz.get("cx", DEFAULT_SLIDE_WIDTH)), int(sldSz.get("cy", DEFAULT_SLIDE_HEIGHT))
    except (TypeError, ValueError):
        return DEFAULT_SLIDE_WIDTH, DEFAULT_SLIDE_HEIGHT


def _resolve_image_bytes(zf: zipfile.ZipFile, slide_name: str, rid: str) -> tuple[bytes, str] | None:
    rels_name = slide_name.replace("slides/", "slides/_rels/") + ".rels"
    if rels_name not in zf.namelist():
        return None
    rels_root = etree.fromstring(zf.read(rels_name))
    target = None
    for rel in rels_root:
        if rel.get("Id") == rid:
            target = rel.get("Target")
            break
    if not target:
        return None
    media_path = os.path.normpath(os.path.join("ppt/slides", target)).replace("\\", "/")
    if media_path not in zf.namelist():
        return None
    ext = media_path.rsplit(".", 1)[-1].lower()
    return zf.read(media_path), ext


def _is_design_notes_group(grp: etree._Element) -> bool:
    blob = " ".join(text_of(el) for el in grp.iter() if local_name(el) == "sp")
    return bool(_DESIGN_NOTE_RE.search(blob))


def _extract_title_parts_from_group(
    grp: etree._Element,
    zf: zipfile.ZipFile,
    slide_name: str,
) -> dict[str, Any] | None:
    """Unpack title banner + heading label + icon from one grpSp on the last design slide."""
    banner_el = None
    label_el = None
    icon_el = None
    icon_off = icon_ext = None
    icon_bytes = icon_file_ext = None

    for inner in grp:
        tag = local_name(inner)
        if tag == "sp":
            geom = prst_geom(inner)
            text = text_of(inner) or ""
            if geom in {"roundRect", "round2SameRect"} and banner_el is None:
                banner_el = inner
            if _TYPE_HEADING_RE.search(text):
                label_el = inner
        elif tag == "pic" and icon_el is None:
            icon_el = inner
            icon_off, icon_ext = off_ext(inner, "p:spPr")
            blip = inner.find(".//" + q("a:blip"))
            rid = blip.get("{%s}embed" % R) if blip is not None else None
            if rid:
                resolved = _resolve_image_bytes(zf, slide_name, rid)
                if resolved:
                    icon_bytes, icon_file_ext = resolved

    if banner_el is None or label_el is None:
        return None

    label_is_separate = banner_el is not label_el
    return {
        "title_banner_el": copy.deepcopy(banner_el),
        "title_label_el": copy.deepcopy(label_el) if label_is_separate else None,
        "title_icon_el": copy.deepcopy(icon_el) if icon_el is not None else None,
        "title_icon_off": icon_off,
        "title_icon_ext": icon_ext,
        "title_icon_image_bytes": icon_bytes,
        "title_icon_image_ext": icon_file_ext,
    }


def _extract_question_parts_from_group(
    grp: etree._Element,
    theme_colors: dict[str, str],
) -> dict[str, Any] | None:
    """Unpack question pill bar + 'Question' label from one grpSp on the MCQ design slide."""
    pill_el = None
    label_el = None

    for inner in grp:
        if local_name(inner) != "sp":
            continue
        geom = prst_geom(inner)
        text = (text_of(inner) or "").strip()
        if geom in {"roundRect", "round2SameRect"} and pill_el is None:
            _, ext = off_ext(inner, "p:spPr")
            if in_range(ext, HEADING_CX, HEADING_CY):
                pill_el = inner
        if _QUESTION_LABEL_RE.match(text):
            label_el = inner

    if pill_el is None or label_el is None:
        return None

    label_is_separate = pill_el is not label_el
    fill = _fill_hex_of(pill_el, theme_colors)
    text_color = _first_run_color(label_el, theme_colors)
    return {
        "question_pill_el": copy.deepcopy(pill_el),
        "question_pill_label_el": copy.deepcopy(label_el) if label_is_separate else None,
        "question_pill_fill": fill,
        "question_pill_text_color": text_color,
    }


def _group_is_question_pill(grp: etree._Element) -> bool:
    for inner in grp:
        if local_name(inner) != "sp":
            continue
        if _QUESTION_LABEL_RE.match((text_of(inner) or "").strip()):
            return True
    return False


def _extract_option_parts_from_group(
    grp: etree._Element,
    theme_colors: dict[str, str],
) -> dict[str, Any] | None:
    """Unpack option pill + label from one grpSp on the MCQ design slide."""
    inner_sps = [c for c in grp if local_name(c) == "sp"]
    pill_el = find_option_pill_el(inner_sps)
    label_el = find_option_label_el(inner_sps, pill_el)
    if pill_el is None or label_el is None:
        return None

    raw_label = (text_of(label_el) or "").strip()
    label_key = parse_option_label(raw_label)
    if label_key is None:
        return None

    fill = _fill_hex_of(pill_el, theme_colors)
    if not fill:
        return None

    off, _ = off_ext(grp, "p:grpSpPr")

    return {
        "option_key": label_key,
        "raw_label": raw_label,
        "top": int(off[1]) if off else 0,
        "option_fill": fill,
        "option_text_color": _first_run_color(label_el, theme_colors),
        "option_pill_group_el": copy.deepcopy(grp),
    }


def _scan_options_on_mcq_slide(
    zf: zipfile.ZipFile,
    slide_name: str,
    theme_colors: dict[str, str],
) -> dict[str, Any] | None:
    """Find grouped option pills (ellipse or roundRect + A/B/1/ii label) on the MCQ design slide."""
    root = etree.fromstring(zf.read(slide_name))
    spTree = root.find(".//" + q("p:spTree"))
    if spTree is None:
        return None

    option_fill: dict[str, str] = {}
    option_text_color = None
    option_group_el = None
    label_samples: list[tuple[int, str]] = []

    for child in spTree:
        if local_name(child) != "grpSp":
            continue
        if _group_is_question_pill(child):
            continue
        found = _extract_option_parts_from_group(child, theme_colors)
        if found is None:
            continue
        option_fill.setdefault(found["option_key"], found["option_fill"])
        option_text_color = option_text_color or found.get("option_text_color")
        if option_group_el is None:
            option_group_el = found["option_pill_group_el"]
        label_samples.append((found.get("top", 0), found.get("raw_label", "")))

    if option_group_el is None:
        return None

    label_samples.sort(key=lambda item: item[0])
    option_labels = option_labels_from_template_samples([raw for _, raw in label_samples])

    return {
        "option_fill": option_fill,
        "option_labels": option_labels,
        "option_text_color": option_text_color,
        "option_pill_group_el": option_group_el,
    }


def _scan_question_pill_on_mcq_slide(
    zf: zipfile.ZipFile,
    slide_name: str,
    theme_colors: dict[str, str],
) -> dict[str, Any] | None:
    """Find grouped question pill (bar + 'Question' label) on the MCQ design slide."""
    root = etree.fromstring(zf.read(slide_name))
    spTree = root.find(".//" + q("p:spTree"))
    if spTree is None:
        return None

    for child in spTree:
        if local_name(child) != "grpSp":
            continue
        found = _extract_question_parts_from_group(child, theme_colors)
        if found is not None:
            return found
    return None


def _scan_title_banner_on_last_slide(zf, sn, slide_width, slide_height):
    """Find grouped title block (banner + heading label + icon) on the last template slide."""
    root = etree.fromstring(zf.read(sn))
    spTree = root.find(".//" + q("p:spTree"))
    if spTree is None:
        return None

    for child in spTree:
        if local_name(child) != "grpSp":
            continue
        if _is_design_notes_group(child):
            continue
        found = _extract_title_parts_from_group(child, zf, sn)
        if found is not None:
            return found
    return None


def scan_template(
    zf: zipfile.ZipFile,
    theme_colors: dict[str, str],
) -> dict[str, Any]:
    """Scan designated template slides for color tokens and cloneable shape XML."""
    question_pill_fill = None
    question_pill_text_color = None
    question_pill_el = None
    question_pill_label_el = None

    option_fill: dict[str, str] = {}
    option_text_color = None
    option_standalone_pill_el = None
    option_standalone_label_el = None
    option_group_el = None

    body_text_color = None

    table_header_fill = None
    table_border_color = None
    table_header_text_color = None
    table_body_text_color = None

    title_banner_el = None
    title_label_el = None
    title_icon_el = None
    title_icon_off = None
    title_icon_ext = None
    title_icon_image_bytes = None
    title_icon_image_ext = None

    slide_width, slide_height = _extract_slide_size(zf)
    # take the slides file from the zip file and sort them by the slide number
    slide_names = sorted(
        (n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )
    # take out the last two slides from all as we decied to do these to prevent large slide scans last two have enough data to need
    design_slide_names = _design_slide_names(slide_names)
    mcq_slide_name = slide_names[resolve_slide_index(MCQ_DESIGN_SLIDE_INDEX, len(slide_names))] if slide_names else None
    title_slide_name = slide_names[resolve_slide_index(TITLE_DESIGN_SLIDE_INDEX, len(slide_names))] if slide_names else None

    # ------------------------------------------------------------------
    # Walk only the 2 design slides (MCQ + title) and read each shape.
    #
    # Slide XML tree (simplified):
    #   p:sld
    #     └── p:cSld
    #           └── p:spTree          ← all shapes live here
    #                 ├── p:sp        ← text box, pill, rectangle
    #                 ├── p:grpSp     ← grouped shapes (pill + label together)
    #                 └── p:graphicFrame  ← table
    # ------------------------------------------------------------------
    for sn in design_slide_names:
        # Read one slide XML file from the zip (e.g. ppt/slides/slide6.xml).
        root = etree.fromstring(zf.read(sn))
        # spTree = the container that holds every shape on this slide.
        spTree = root.find(".//" + q("p:spTree"))
        if spTree is None:
            continue
        # Direct children = top-level shapes in draw order (bottom to top).
        children = list(spTree)

        for i, child in enumerate(children):
            # XML tag without namespace, e.g. "sp", "pic", "grpSp".
            tag = local_name(child)

            # --- p:sp = a normal PowerPoint shape (box, circle, text) -----
            if tag == "sp":
                # prstGeom tells shape type: roundRect, ellipse, rect, etc.
                geom = prst_geom(child)
                # off = (x, y) position, ext = (width, height) in EMU units.
                off, ext = off_ext(child, "p:spPr")
                text = text_of(child)

                # Body paragraph color: any other text shape with meaningful text.
                if geom not in (None, "roundRect", "ellipse") and text and len(text) > 3 and body_text_color is None:
                    c = _first_run_color(child, theme_colors)
                    if c:
                        body_text_color = c
                elif geom is None and text and len(text) > 3 and body_text_color is None:
                    c = _first_run_color(child, theme_colors)
                    if c:
                        body_text_color = c

            # --- p:graphicFrame = table -------------------------------------
            elif tag == "graphicFrame":
                tbl = child.find(".//" + q("a:tbl"))
                if tbl is not None and table_header_fill is None:
                    trs = tbl.findall(q("a:tr"))  # table rows
                    if trs:
                        header_tc = trs[0].find(q("a:tc"))  # first row = header
                        if header_tc is not None:
                            tcPr = header_tc.find(q("a:tcPr"))  # cell properties
                            if tcPr is not None:
                                fill = _resolve_color(tcPr.find(q("a:solidFill")), theme_colors)
                                if fill:
                                    table_header_fill = fill
                                # Read border color from left/top/right/bottom line.
                                for border_tag in ("lnL", "lnT", "lnR", "lnB"):
                                    ln = tcPr.find(q(f"a:{border_tag}"))
                                    if ln is not None:
                                        bc = _resolve_color(ln.find(q("a:solidFill")), theme_colors)
                                        if bc:
                                            table_border_color = bc
                                            break
                            c = _first_run_color(header_tc, theme_colors)
                            if c:
                                table_header_text_color = c
                        if len(trs) > 1:
                            body_tc = trs[1].find(q("a:tc"))  # second row = body sample
                            if body_tc is not None:
                                c = _first_run_color(body_tc, theme_colors)
                                if c:
                                    table_body_text_color = c

    if mcq_slide_name:
        found = _scan_question_pill_on_mcq_slide(zf, mcq_slide_name, theme_colors)
        if found:
            question_pill_el = found["question_pill_el"]
            question_pill_label_el = found["question_pill_label_el"]
            if found.get("question_pill_fill"):
                question_pill_fill = found["question_pill_fill"]
            if found.get("question_pill_text_color"):
                question_pill_text_color = found["question_pill_text_color"]

        options = _scan_options_on_mcq_slide(zf, mcq_slide_name, theme_colors)
        option_labels: list[str] = []
        if options:
            option_fill.update(options["option_fill"])
            option_group_el = options["option_pill_group_el"]
            option_labels = options.get("option_labels") or []
            if options.get("option_text_color"):
                option_text_color = options["option_text_color"]

    if title_slide_name:
        found = _scan_title_banner_on_last_slide(
            zf, title_slide_name, slide_width, slide_height,
        )
        if found:
            title_banner_el = found["title_banner_el"]
            title_label_el = found["title_label_el"]
            title_icon_el = found["title_icon_el"]
            title_icon_off = found["title_icon_off"]
            title_icon_ext = found["title_icon_ext"]
            title_icon_image_bytes = found["title_icon_image_bytes"]
            title_icon_image_ext = found["title_icon_image_ext"]
            fill = _fill_hex_of(title_banner_el, theme_colors)
            if fill:
                question_pill_fill = fill

    nt_color = _parse_normal_text_color_from_last_slide(zf)
    if nt_color:
        body_text_color = nt_color
    tokens = {
        "question_pill_fill": question_pill_fill or DEFAULT_QUESTION_PILL_FILL,
        "question_pill_text_color": question_pill_text_color or DEFAULT_QUESTION_PILL_TEXT_COLOR,
        "option_fill": option_fill or {"shared": question_pill_fill or DEFAULT_QUESTION_PILL_FILL},
        "option_labels": option_labels or build_template_option_labels("upper_alpha"),
        "option_text_color": option_text_color or DEFAULT_OPTION_TEXT_COLOR,
        "table_header_fill": table_header_fill or question_pill_fill or DEFAULT_TABLE_HEADER_FILL,
        "table_border_color": table_border_color or DEFAULT_TABLE_BORDER_COLOR,
        "table_header_text_color": table_header_text_color or question_pill_text_color or DEFAULT_TABLE_HEADER_TEXT_COLOR,
        "table_body_text_color": table_body_text_color or DEFAULT_TABLE_BODY_TEXT_COLOR,
        "body_text_color": body_text_color or question_pill_text_color or DEFAULT_QUESTION_PILL_TEXT_COLOR,
        "accent": question_pill_fill or theme_colors.get("accent1") or DEFAULT_ACCENT,
    }

    return {
        "tokens": tokens,
        "question_pill_el": question_pill_el,
        "question_pill_label_el": question_pill_label_el,
        "option_pill_standalone_el": option_standalone_pill_el,
        "option_label_standalone_el": option_standalone_label_el,
        "option_pill_group_el": option_group_el,
        "title_banner_el": title_banner_el,
        "title_label_el": title_label_el,
        "title_icon_el": title_icon_el,
        "title_icon_off": title_icon_off,
        "title_icon_ext": title_icon_ext,
        "title_icon_image_bytes": title_icon_image_bytes,
        "title_icon_image_ext": title_icon_image_ext,
    }
