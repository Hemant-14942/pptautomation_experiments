"""
Heuristic scan of template .pptx zip for design tokens and cloneable shapes.

Finds: question pill, option pills, logo, question icon, title banner, table colors.
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
    DEFAULT_FONT,
    DEFAULT_HEADING_FILL,
    DEFAULT_HEADING_TEXT_COLOR,
    DEFAULT_OPTION_TEXT_COLOR,
    DEFAULT_TABLE_BODY_TEXT_COLOR,
    DEFAULT_TABLE_BORDER_COLOR,
    DEFAULT_TABLE_HEADER_FILL,
    DEFAULT_TABLE_HEADER_TEXT_COLOR,
)
from app.dynamic_rendering.constants.presentation_defaults import (
    DEFAULT_SLIDE_HEIGHT,
    DEFAULT_SLIDE_WIDTH,
)
from app.dynamic_rendering.constants.shape_geometry import (
    HEADING_CX,
    HEADING_CY,
    ICON_MAX_SIZE_FRACTION,
    ICON_ZONE_X_FRACTION,
    LOGO_CX,
    LOGO_CY,
    OPTION_CX,
    OPTION_CY,
)
from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.utils.xml.helpers import (
    font_size_pt,
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
_QUESTION_LABEL_RE = re.compile(r"^\s*question\s*$", re.I)


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
        if v.startswith("sys:"):
            v = v[4:]
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


def _first_run_style(
    container: etree._Element,
    theme_colors: dict[str, str],
) -> tuple[str | None, str | None]:
    rPr = representative_rpr(container)
    if rPr is None:
        return None, None
    color = _resolve_color(rPr.find(q("a:solidFill")), theme_colors)
    latin = rPr.find(q("a:latin"))
    font = latin.get("typeface") if latin is not None else None
    return color, font


def _parse_normal_text_from_last_slide(zf: zipfile.ZipFile) -> tuple[str | None, str | None]:
    names = sorted(
        (n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )
    if not names:
        return None, None
    root = etree.fromstring(zf.read(names[-1]))
    blob = " ".join(text_of(el) for el in root.iter() if local_name(el) in {"sp", "grpSp"})
    if "for normal text" not in blob.lower():
        return None, None
    color = None
    font = None
    m = re.search(r"For Normal Text.{0,120}?Font Color\s*:\s*#([0-9A-Fa-f]{6})", blob, re.I | re.S)
    if not m:
        m = re.search(r"Font Color\s*:\s*#([0-9A-Fa-f]{6}).{0,80}?For Normal Text", blob, re.I | re.S)
    if m:
        color = m.group(1).upper()
    m = re.search(r"For Normal Text.{0,120}?Font Type\s*:\s*([A-Za-z][A-Za-z0-9 ]+)", blob, re.I | re.S)
    if not m:
        m = re.search(r"Font Type\s*:\s*([A-Za-z][A-Za-z0-9 ]+).{0,80}?For Normal Text", blob, re.I | re.S)
    if m:
        font = m.group(1).strip().replace(" Bold", "").replace(" Italic", "")
    return color, font


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


def _rects_overlap_y(a_off, a_ext, b_off, b_ext) -> bool:
    if not (a_off and a_ext and b_off and b_ext):
        return False
    return a_off[1] < b_off[1] + b_ext[1] and a_off[1] + a_ext[1] > b_off[1]


def _question_pill_box(children):
    for child in children:
        if local_name(child) != "sp" or prst_geom(child) != "roundRect":
            continue
        if not _QUESTION_LABEL_RE.search(text_of(child) or ""):
            continue
        return off_ext(child, "p:spPr")
    return None, None


def _scan_title_banner_on_last_slide(zf, sn, slide_width, slide_height):
    root = etree.fromstring(zf.read(sn))
    spTree = root.find(".//" + q("p:spTree"))
    if spTree is None:
        return None
    children = [c for c in list(spTree) if local_name(c) in {"sp", "pic", "grpSp"}]

    label_el = label_off = label_ext = None
    for child in children:
        if local_name(child) != "sp":
            continue
        off, ext = off_ext(child, "p:spPr")
        if not off or off[1] >= slide_height * 0.35 or off[0] >= slide_width * 0.45:
            continue
        if _TYPE_HEADING_RE.search(text_of(child) or ""):
            label_el = child
            label_off, label_ext = off, ext
            break
    if label_el is None:
        return None

    banner_el = label_el if prst_geom(label_el) == "roundRect" else None
    banner_off, banner_ext = label_off, label_ext
    if banner_el is None:
        best = None
        for child in children:
            if local_name(child) != "sp" or child is label_el:
                continue
            if prst_geom(child) not in {"roundRect", "round2SameRect"}:
                continue
            off, ext = off_ext(child, "p:spPr")
            if not off or off[1] >= slide_height * 0.45:
                continue
            if not _rects_overlap_y(off, ext, label_off, label_ext):
                continue
            best = (child, off, ext)
            break
        if best is None:
            return None
        banner_el, banner_off, banner_ext = best

    icon_el = icon_off = icon_ext = None
    icon_bytes = icon_file_ext = None
    for c in children:
        tag = local_name(c)
        if tag not in {"pic", "grpSp"}:
            continue
        pref = "p:grpSpPr" if tag == "grpSp" else "p:spPr"
        c_off, c_ext = off_ext(c, pref)
        if not c_off or not c_ext:
            continue
        if c_off[0] + c_ext[0] / 2 >= slide_width * ICON_ZONE_X_FRACTION:
            continue
        if c_ext[0] >= slide_width * ICON_MAX_SIZE_FRACTION or c_ext[1] >= slide_height * ICON_MAX_SIZE_FRACTION:
            continue
        if not _rects_overlap_y(c_off, c_ext, banner_off, banner_ext):
            continue
        icon_el, icon_off, icon_ext = c, c_off, c_ext
        blip = c.find(".//" + q("a:blip"))
        rid = blip.get("{%s}embed" % R) if blip is not None else None
        if rid:
            resolved = _resolve_image_bytes(zf, sn, rid)
            if resolved:
                icon_bytes, icon_file_ext = resolved
        break

    label_is_separate = banner_el is not label_el
    return {
        "title_banner_el": copy.deepcopy(banner_el),
        "title_label_el": copy.deepcopy(label_el) if label_is_separate else None,
        "title_icon_el": copy.deepcopy(icon_el) if icon_el is not None else None,
        "title_icon_off": icon_off,
        "title_icon_ext": icon_ext,
        "title_icon_image_bytes": icon_bytes,
        "title_icon_image_ext": icon_file_ext,
        "title_heading_font_size_pt": font_size_pt(label_el),
    }


def scan_template(
    zf: zipfile.ZipFile,
    theme_colors: dict[str, str],
    theme_font: str | None,
) -> dict[str, Any]:
    """Walk all template slides and return tokens + cloneable shape XML."""
    heading_fill = None
    heading_text_color = None
    heading_font = None
    heading_pill_el = None
    heading_label_el = None

    option_fill: dict[str, str] = {}
    option_text_color = None
    option_font = None
    option_standalone_pill_el = None
    option_standalone_label_el = None
    option_group_el = None

    body_text_color = None

    table_header_fill = None
    table_border_color = None
    table_header_text_color = None
    table_body_text_color = None

    logo_el = None
    logo_off = None
    logo_ext = None
    logo_image_bytes = None
    logo_image_ext = None

    question_icon_el = None
    question_icon_off = None
    question_icon_ext = None
    question_icon_image_bytes = None
    question_icon_image_ext = None

    title_banner_el = None
    title_label_el = None
    title_icon_el = None
    title_icon_off = None
    title_icon_ext = None
    title_icon_image_bytes = None
    title_icon_image_ext = None
    title_heading_font_size_pt = None

    slide_width, slide_height = _extract_slide_size(zf)

    slide_names = sorted(
        (n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )

    for sn in slide_names:
        root = etree.fromstring(zf.read(sn))
        spTree = root.find(".//" + q("p:spTree"))
        if spTree is None:
            continue
        children = list(spTree)

        for i, child in enumerate(children):
            tag = local_name(child)

            if tag == "sp":
                geom = prst_geom(child)
                off, ext = off_ext(child, "p:spPr")
                text = text_of(child)

                if geom == "roundRect" and in_range(ext, HEADING_CX, HEADING_CY) and heading_pill_el is None:
                    fill = _fill_hex_of(child, theme_colors)
                    if fill:
                        heading_fill = fill
                        heading_pill_el = copy.deepcopy(child)
                        pill_text = text_of(child)
                        if pill_text:
                            heading_text_color, heading_font = _first_run_style(child, theme_colors)
                        else:
                            nxt = children[i + 1] if i + 1 < len(children) else None
                            if nxt is not None and local_name(nxt) == "sp" and text_of(nxt):
                                heading_text_color, heading_font = _first_run_style(nxt, theme_colors)
                                heading_label_el = copy.deepcopy(nxt)

                elif geom == "ellipse" and in_range(ext, OPTION_CX, OPTION_CY):
                    fill = _fill_hex_of(child, theme_colors)
                    nxt = children[i + 1] if i + 1 < len(children) else None
                    label_text = text_of(nxt) if nxt is not None and local_name(nxt) == "sp" else ""
                    letter = label_text.strip()[:1].upper()
                    if fill and letter.isalpha():
                        option_fill.setdefault(letter, fill)
                    if fill and option_standalone_pill_el is None:
                        option_standalone_pill_el = copy.deepcopy(child)
                        if nxt is not None and local_name(nxt) == "sp":
                            option_standalone_label_el = copy.deepcopy(nxt)
                            c, f = _first_run_style(nxt, theme_colors)
                            option_text_color = option_text_color or c
                            option_font = option_font or f

                elif geom not in (None, "roundRect", "ellipse") and text and len(text) > 3 and body_text_color is None:
                    c, _f = _first_run_style(child, theme_colors)
                    if c:
                        body_text_color = c
                elif geom is None and text and len(text) > 3 and body_text_color is None:
                    c, _f = _first_run_style(child, theme_colors)
                    if c:
                        body_text_color = c

            elif tag == "grpSp":
                inner_sps = [c for c in child if local_name(c) == "sp"]
                pill_el = next((c for c in inner_sps if prst_geom(c) == "ellipse"), None)
                label_el = next((c for c in inner_sps if c is not pill_el and text_of(c)), None)
                if pill_el is not None and label_el is not None:
                    _, pill_ext = off_ext(pill_el, "p:spPr")
                    if in_range(pill_ext, OPTION_CX, OPTION_CY):
                        fill = _fill_hex_of(pill_el, theme_colors)
                        letter = text_of(label_el).strip()[:1].upper()
                        if fill and letter.isalpha():
                            option_fill.setdefault(letter, fill)
                        if fill and option_group_el is None:
                            option_group_el = copy.deepcopy(child)
                            c, f = _first_run_style(label_el, theme_colors)
                            option_text_color = option_text_color or c
                            option_font = option_font or f

            elif tag == "graphicFrame":
                tbl = child.find(".//" + q("a:tbl"))
                if tbl is not None and table_header_fill is None:
                    trs = tbl.findall(q("a:tr"))
                    if trs:
                        header_tc = trs[0].find(q("a:tc"))
                        if header_tc is not None:
                            tcPr = header_tc.find(q("a:tcPr"))
                            if tcPr is not None:
                                fill = _resolve_color(tcPr.find(q("a:solidFill")), theme_colors)
                                if fill:
                                    table_header_fill = fill
                                for border_tag in ("lnL", "lnT", "lnR", "lnB"):
                                    ln = tcPr.find(q(f"a:{border_tag}"))
                                    if ln is not None:
                                        bc = _resolve_color(ln.find(q("a:solidFill")), theme_colors)
                                        if bc:
                                            table_border_color = bc
                                            break
                            c, _f = _first_run_style(header_tc, theme_colors)
                            if c:
                                table_header_text_color = c
                        if len(trs) > 1:
                            body_tc = trs[1].find(q("a:tc"))
                            if body_tc is not None:
                                c, _f = _first_run_style(body_tc, theme_colors)
                                if c:
                                    table_body_text_color = c

            elif tag == "pic":
                off, ext = off_ext(child, "p:spPr")
                if not (ext and in_range(ext, LOGO_CX, LOGO_CY)):
                    continue
                blip = child.find(".//" + q("a:blip"))
                rid = blip.get("{%s}embed" % R) if blip is not None else None
                if not rid:
                    continue
                resolved = _resolve_image_bytes(zf, sn, rid)
                if not resolved:
                    continue
                q_off, q_ext = _question_pill_box(children)
                if q_off and _rects_overlap_y(off, ext, q_off, q_ext):
                    if question_icon_el is None:
                        question_icon_el = copy.deepcopy(child)
                        question_icon_off, question_icon_ext = off, ext
                        question_icon_image_bytes, question_icon_image_ext = resolved
                    continue
                if off[0] + ext[0] / 2 < slide_width * 0.5:
                    continue
                if logo_el is None:
                    logo_el = copy.deepcopy(child)
                    logo_off, logo_ext = off, ext
                    logo_image_bytes, logo_image_ext = resolved

    if slide_names:
        found = _scan_title_banner_on_last_slide(
            zf, slide_names[-1], slide_width, slide_height,
        )
        if found:
            title_banner_el = found["title_banner_el"]
            title_label_el = found["title_label_el"]
            title_icon_el = found["title_icon_el"]
            title_icon_off = found["title_icon_off"]
            title_icon_ext = found["title_icon_ext"]
            title_icon_image_bytes = found["title_icon_image_bytes"]
            title_icon_image_ext = found["title_icon_image_ext"]
            title_heading_font_size_pt = found["title_heading_font_size_pt"]
            fill = _fill_hex_of(title_banner_el, theme_colors)
            if fill:
                heading_fill = fill
            if (
                logo_off
                and title_icon_off
                and abs(logo_off[0] - title_icon_off[0]) < 200_000
                and abs(logo_off[1] - title_icon_off[1]) < 200_000
            ):
                logo_el = logo_off = logo_ext = None
                logo_image_bytes = logo_image_ext = None

    nt_color, nt_font = _parse_normal_text_from_last_slide(zf)
    if nt_color:
        body_text_color = nt_color
    body_font = nt_font
    tokens = {
        "heading_fill": heading_fill or DEFAULT_HEADING_FILL,
        "heading_text_color": heading_text_color or DEFAULT_HEADING_TEXT_COLOR,
        "heading_font": heading_font or theme_font or DEFAULT_FONT,
        "option_fill": option_fill or {"shared": heading_fill or DEFAULT_HEADING_FILL},
        "option_text_color": option_text_color or DEFAULT_OPTION_TEXT_COLOR,
        "option_font": option_font or theme_font or DEFAULT_FONT,
        "table_header_fill": table_header_fill or heading_fill or DEFAULT_TABLE_HEADER_FILL,
        "table_border_color": table_border_color or DEFAULT_TABLE_BORDER_COLOR,
        "table_header_text_color": table_header_text_color or DEFAULT_TABLE_HEADER_TEXT_COLOR,
        "table_body_text_color": table_body_text_color or DEFAULT_TABLE_BODY_TEXT_COLOR,
        "body_text_color": body_text_color or heading_text_color or DEFAULT_HEADING_TEXT_COLOR,
        "body_font": body_font or heading_font or DEFAULT_FONT,
        "accent": heading_fill or theme_colors.get("accent1") or DEFAULT_ACCENT,
    }

    return {
        "tokens": tokens,
        "heading_pill_el": heading_pill_el,
        "heading_label_el": heading_label_el,
        "option_pill_standalone_el": option_standalone_pill_el,
        "option_label_standalone_el": option_standalone_label_el,
        "option_pill_group_el": option_group_el,
        "logo_el": logo_el,
        "logo_off": logo_off,
        "logo_ext": logo_ext,
        "logo_image_bytes": logo_image_bytes,
        "logo_image_ext": logo_image_ext,
        "question_icon_el": question_icon_el,
        "question_icon_off": question_icon_off,
        "question_icon_ext": question_icon_ext,
        "question_icon_image_bytes": question_icon_image_bytes,
        "question_icon_image_ext": question_icon_image_ext,
        "title_banner_el": title_banner_el,
        "title_label_el": title_label_el,
        "title_icon_el": title_icon_el,
        "title_icon_off": title_icon_off,
        "title_icon_ext": title_icon_ext,
        "title_icon_image_bytes": title_icon_image_bytes,
        "title_icon_image_ext": title_icon_image_ext,
        "title_heading_font_size_pt": title_heading_font_size_pt,
    }
