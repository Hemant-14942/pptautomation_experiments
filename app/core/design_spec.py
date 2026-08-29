from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import zipfile
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from lxml import etree

from app.ai.azure_ai_client import chat
from app.constants.design_tokens_defaults import (
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
from app.constants.shape_geometry import (
    HEADING_CX,
    HEADING_CY,
    ICON_MAX_SIZE_FRACTION,
    ICON_ZONE_X_FRACTION,
    LOGO_CX,
    LOGO_CY,
    OPTION_CX,
    OPTION_CY,
    TITLE_BANNER_WIDTH_FRACTION,
)
from app.constants.xml_namespaces import NS, R
from app.core.style_parser import _extract_theme
from app.prompts.design_tokens_prompts import (
    DESIGN_TOKENS_SYSTEM_PROMPT,
    build_design_tokens_prompt,
)
from app.utils.xml_helpers import (
    in_range as _in_range,
    local_name as _local,
    off_ext as _off_ext,
    prst_geom as _prst_geom,
    q as _q,
    text_of as _text_of,
)

_SCHEME_ALIAS = {"tx1": "dk1", "bg1": "lt1", "tx2": "dk2", "bg2": "lt2"}
_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")

_memory_cache: dict[str, "DesignSpec"] = {}


@dataclass
class DesignSpec:
    heading_fill: str
    heading_text_color: str
    heading_font: str | None
    option_fill: dict[str, str]
    option_text_color: str
    option_font: str | None
    table_header_fill: str
    table_border_color: str
    table_header_text_color: str
    table_body_text_color: str
    body_text_color: str
    accent: str
    source: str = "heuristic"

    heading_pill_el: etree._Element | None = None
    heading_label_el: etree._Element | None = None
    option_pill_standalone_el: etree._Element | None = None
    option_label_standalone_el: etree._Element | None = None
    option_pill_group_el: etree._Element | None = None
    logo_el: etree._Element | None = None
    logo_off: tuple[int, int] | None = None
    logo_ext: tuple[int, int] | None = None
    logo_image_bytes: bytes | None = None
    logo_image_ext: str | None = None

    # Topic-title banner heading: a wide rounded bar + its corner icon
    # picture, distinct from the compact MCQ heading_pill_el above.
    title_banner_el: etree._Element | None = None
    title_label_el: etree._Element | None = None
    title_icon_el: etree._Element | None = None
    title_icon_off: tuple[int, int] | None = None
    title_icon_ext: tuple[int, int] | None = None
    title_icon_image_bytes: bytes | None = None
    title_icon_image_ext: str | None = None

    def option_color_for(self, letter: str) -> str:
        letter = (letter or "").upper()
        if letter in self.option_fill:
            return self.option_fill[letter]
        if "shared" in self.option_fill:
            return self.option_fill["shared"]
        return self.accent


# --------------------------------------------------------------------------
# small XML helpers specific to this module's color/style resolution
# --------------------------------------------------------------------------

def _resolve_color(container: etree._Element | None, theme_colors: dict[str, str]) -> str | None:
    if container is None:
        return None
    srgb = container.find(_q("a:srgbClr"))
    if srgb is not None:
        v = srgb.get("val", "")
        return v.upper() if _HEX_RE.match(v) else None
    scheme = container.find(_q("a:schemeClr"))
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
    spPr = sp.find(_q("p:spPr"))
    if spPr is None:
        return None
    return _resolve_color(spPr.find(_q("a:solidFill")), theme_colors)


def _first_run_style(container: etree._Element, theme_colors: dict[str, str]) -> tuple[str | None, str | None]:
    """Best-effort (color, font) from the first run (or defRPr) in a
    shape's or table cell's text body. Handles both <p:txBody> (shapes)
    and <a:txBody> (table cells)."""
    txBody = container.find(_q("p:txBody"))
    if txBody is None:
        txBody = container.find(_q("a:txBody"))
    if txBody is None:
        return None, None
    r = txBody.find(".//" + _q("a:r"))
    rPr = r.find(_q("a:rPr")) if r is not None else None
    if rPr is None:
        rPr = txBody.find(_q("a:lstStyle") + "/" + _q("a:defRPr"))
    if rPr is None:
        rPr = txBody.find(".//" + _q("a:endParaRPr"))
    if rPr is None:
        return None, None
    color = _resolve_color(rPr.find(_q("a:solidFill")), theme_colors)
    latin = rPr.find(_q("a:latin"))
    font = latin.get("typeface") if latin is not None else None
    return color, font


def _set_hex(d: dict[str, Any], key: str, value: str | None) -> None:
    if value:
        d[key] = value


# --------------------------------------------------------------------------
# heuristic scan of the template zip
# --------------------------------------------------------------------------

def _extract_slide_size(zf: zipfile.ZipFile) -> tuple[int, int]:
    """(cx, cy) of the deck's own slide size, so shape-role heuristics can
    scale with decks that use a non-standard (e.g. Google Slides 4x) canvas
    instead of PowerPoint's ~12,192,000 EMU default width."""
    if "ppt/presentation.xml" not in zf.namelist():
        return 12_192_000, 6_858_000
    root = etree.fromstring(zf.read("ppt/presentation.xml"))
    sldSz = root.find(_q("p:sldSz"))
    if sldSz is None:
        return 12_192_000, 6_858_000
    try:
        return int(sldSz.get("cx", 12_192_000)), int(sldSz.get("cy", 6_858_000))
    except (TypeError, ValueError):
        return 12_192_000, 6_858_000


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


def _scan_template(zf: zipfile.ZipFile, theme_colors: dict[str, str], theme_font: str | None) -> dict[str, Any]:
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

    title_banner_el = None
    title_label_el = None
    title_icon_el = None
    title_icon_off = None
    title_icon_ext = None
    title_icon_image_bytes = None
    title_icon_image_ext = None

    slide_width, slide_height = _extract_slide_size(zf)

    slide_names = sorted(
        (n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )

    for sn in slide_names:
        root = etree.fromstring(zf.read(sn))
        spTree = root.find(".//" + _q("p:spTree"))
        if spTree is None:
            continue
        children = list(spTree)

        banner_off = banner_ext = None
        banner_found_this_slide = False

        for i, child in enumerate(children):
            tag = _local(child)

            if tag == "sp":
                geom = _prst_geom(child)
                off, ext = _off_ext(child, "p:spPr")
                text = _text_of(child)

                if geom == "roundRect" and _in_range(ext, HEADING_CX, HEADING_CY) and heading_pill_el is None:
                    fill = _fill_hex_of(child, theme_colors)
                    if fill:
                        heading_fill = fill
                        heading_pill_el = copy.deepcopy(child)
                        nxt = children[i + 1] if i + 1 < len(children) else None
                        if nxt is not None and _local(nxt) == "sp":
                            heading_text_color, heading_font = _first_run_style(nxt, theme_colors)
                            heading_label_el = copy.deepcopy(nxt)

                elif (
                    geom == "roundRect"
                    and title_banner_el is None
                    and ext
                    and ext[0] >= slide_width * TITLE_BANNER_WIDTH_FRACTION
                ):
                    title_banner_el = copy.deepcopy(child)
                    banner_off, banner_ext = off, ext
                    banner_found_this_slide = True
                    nxt = children[i + 1] if i + 1 < len(children) else None
                    if nxt is not None and _local(nxt) == "sp":
                        title_label_el = copy.deepcopy(nxt)

                elif geom == "ellipse" and _in_range(ext, OPTION_CX, OPTION_CY):
                    fill = _fill_hex_of(child, theme_colors)
                    nxt = children[i + 1] if i + 1 < len(children) else None
                    label_text = _text_of(nxt) if nxt is not None and _local(nxt) == "sp" else ""
                    letter = label_text.strip()[:1].upper()
                    if fill and letter.isalpha():
                        option_fill.setdefault(letter, fill)
                    if fill and option_standalone_pill_el is None:
                        option_standalone_pill_el = copy.deepcopy(child)
                        if nxt is not None and _local(nxt) == "sp":
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
                inner_sps = [c for c in child if _local(c) == "sp"]
                pill_el = next((c for c in inner_sps if _prst_geom(c) == "ellipse"), None)
                label_el = next((c for c in inner_sps if c is not pill_el and _text_of(c)), None)
                if pill_el is not None and label_el is not None:
                    _, pill_ext = _off_ext(pill_el, "p:spPr")
                    if _in_range(pill_ext, OPTION_CX, OPTION_CY):
                        fill = _fill_hex_of(pill_el, theme_colors)
                        letter = _text_of(label_el).strip()[:1].upper()
                        if fill and letter.isalpha():
                            option_fill.setdefault(letter, fill)
                        if fill and option_group_el is None:
                            option_group_el = copy.deepcopy(child)
                            c, f = _first_run_style(label_el, theme_colors)
                            option_text_color = option_text_color or c
                            option_font = option_font or f

            elif tag == "graphicFrame":
                tbl = child.find(".//" + _q("a:tbl"))
                if tbl is not None and table_header_fill is None:
                    trs = tbl.findall(_q("a:tr"))
                    if trs:
                        header_tc = trs[0].find(_q("a:tc"))
                        if header_tc is not None:
                            tcPr = header_tc.find(_q("a:tcPr"))
                            if tcPr is not None:
                                fill = _resolve_color(tcPr.find(_q("a:solidFill")), theme_colors)
                                if fill:
                                    table_header_fill = fill
                                for border_tag in ("lnL", "lnT", "lnR", "lnB"):
                                    ln = tcPr.find(_q(f"a:{border_tag}"))
                                    if ln is not None:
                                        bc = _resolve_color(ln.find(_q("a:solidFill")), theme_colors)
                                        if bc:
                                            table_border_color = bc
                                            break
                            c, _f = _first_run_style(header_tc, theme_colors)
                            if c:
                                table_header_text_color = c
                        if len(trs) > 1:
                            body_tc = trs[1].find(_q("a:tc"))
                            if body_tc is not None:
                                c, _f = _first_run_style(body_tc, theme_colors)
                                if c:
                                    table_body_text_color = c

            elif tag == "pic":
                off, ext = _off_ext(child, "p:spPr")
                if logo_el is None and ext and _in_range(ext, LOGO_CX, LOGO_CY):
                    blip = child.find(".//" + _q("a:blip"))
                    rid = blip.get("{%s}embed" % R) if blip is not None else None
                    if rid:
                        resolved = _resolve_image_bytes(zf, sn, rid)
                        if resolved:
                            logo_el = copy.deepcopy(child)
                            logo_off, logo_ext = off, ext
                            logo_image_bytes, logo_image_ext = resolved

        # The title banner's corner icon is a plain `pic` (no separate
        # vector badge in this template's own vocabulary) sitting in the
        # slide's left zone, vertically overlapping the banner -- as
        # opposed to a logo/decoration parked over on the right. Only look
        # for it right after finding the banner for the first time, using
        # that slide's own children so ordering/z-index doesn't matter.
        if banner_found_this_slide and title_icon_el is None:
            for c in children:
                if _local(c) != "pic":
                    continue
                c_off, c_ext = _off_ext(c, "p:spPr")
                if not c_off or not c_ext:
                    continue
                c_cx_center = c_off[0] + c_ext[0] / 2
                if c_cx_center >= slide_width * ICON_ZONE_X_FRACTION:
                    continue
                if c_ext[0] >= slide_width * ICON_MAX_SIZE_FRACTION or c_ext[1] >= slide_height * ICON_MAX_SIZE_FRACTION:
                    continue
                if not (c_off[1] < banner_off[1] + banner_ext[1] and c_off[1] + c_ext[1] > banner_off[1]):
                    continue
                blip = c.find(".//" + _q("a:blip"))
                rid = blip.get("{%s}embed" % R) if blip is not None else None
                if not rid:
                    continue
                resolved = _resolve_image_bytes(zf, sn, rid)
                if not resolved:
                    continue
                title_icon_el = copy.deepcopy(c)
                title_icon_off, title_icon_ext = c_off, c_ext
                title_icon_image_bytes, title_icon_image_ext = resolved
                break

    tokens = {
        "heading_fill": heading_fill or DEFAULT_HEADING_FILL,
        "heading_text_color": heading_text_color or DEFAULT_HEADING_TEXT_COLOR,
        "heading_font": heading_font or theme_font or DEFAULT_FONT,
        "option_fill": option_fill or {"shared": heading_fill or DEFAULT_HEADING_FILL},
        "option_text_color": option_text_color or DEFAULT_OPTION_TEXT_COLOR,
        "option_font": option_font or theme_font or DEFAULT_FONT,
        "table_header_fill": table_header_fill or DEFAULT_TABLE_HEADER_FILL,
        "table_border_color": table_border_color or DEFAULT_TABLE_BORDER_COLOR,
        "table_header_text_color": table_header_text_color or DEFAULT_TABLE_HEADER_TEXT_COLOR,
        "table_body_text_color": table_body_text_color or DEFAULT_TABLE_BODY_TEXT_COLOR,
        "body_text_color": body_text_color or heading_text_color or DEFAULT_HEADING_TEXT_COLOR,
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
        "title_banner_el": title_banner_el,
        "title_label_el": title_label_el,
        "title_icon_el": title_icon_el,
        "title_icon_off": title_icon_off,
        "title_icon_ext": title_icon_ext,
        "title_icon_image_bytes": title_icon_image_bytes,
        "title_icon_image_ext": title_icon_image_ext,
    }


# --------------------------------------------------------------------------
# Azure AI: single call per template to confirm/normalize the tokens
# --------------------------------------------------------------------------

def _ask_azure_for_tokens(heuristic_tokens: dict[str, Any], deployment: str | None = None) -> dict[str, Any] | None:
    prompt = build_design_tokens_prompt(heuristic_tokens)
    try:
        response = chat(
            prompt=prompt,
            deployment=deployment,
            max_tokens=1024,
            system=DESIGN_TOKENS_SYSTEM_PROMPT,
        )
        text = "".join(getattr(block, "text", "") for block in response.content)
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return json.loads(text[start : end + 1])
    except Exception as exc:  # noqa: BLE001 - never let a bad AI response crash the pipeline
        print(f"[design-spec] azure design-token call failed, using heuristic values ({exc})")
        return None


def _hexish(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.lstrip("#").upper()
    return v if _HEX_RE.match(v) else None


def _merge_ai(heuristic: dict[str, Any], ai: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(heuristic)
    merged["option_fill"] = dict(heuristic.get("option_fill") or {})
    if not isinstance(ai, dict):
        return merged

    hp = ai.get("heading_pill") if isinstance(ai.get("heading_pill"), dict) else {}
    _set_hex(merged, "heading_fill", _hexish(hp.get("fill")))
    _set_hex(merged, "heading_text_color", _hexish(hp.get("text_color")))
    if isinstance(hp.get("font"), str) and hp.get("font"):
        merged["heading_font"] = hp["font"]

    op = ai.get("option_pills") if isinstance(ai.get("option_pills"), dict) else {}
    cleaned: dict[str, str] = {}
    for k, v in op.items():
        hexval = _hexish(v)
        if not hexval:
            continue
        key = "shared" if str(k).lower() == "shared" else str(k).upper()
        cleaned[key] = hexval
    if cleaned:
        merged["option_fill"] = cleaned

    tb = ai.get("table") if isinstance(ai.get("table"), dict) else {}
    _set_hex(merged, "table_header_fill", _hexish(tb.get("header_fill")))
    _set_hex(merged, "table_border_color", _hexish(tb.get("border")))
    _set_hex(merged, "table_header_text_color", _hexish(tb.get("text_color")))

    _set_hex(merged, "accent", _hexish(ai.get("accent")))
    return merged


# --------------------------------------------------------------------------
# public entry point
# --------------------------------------------------------------------------

def get_design_spec(
    template_path: str,
    deployment: str | None = None,
    force_refresh: bool = False,
) -> DesignSpec:
    """Return the (cached) DesignSpec for a template.

    * In-memory cache keyed by (abs path, content hash): repeat calls in
      the same process never re-scan or re-call AI.
    * On-disk cache `<template_path>.designspec.json` keyed by content
      hash: repeat *process* runs never re-call AI for an unchanged
      template file. The cloned shape geometry is re-derived from the
      template on every call (cheap, deterministic, no AI involved).
    """
    abs_path = os.path.abspath(template_path)
    with open(abs_path, "rb") as fh:
        data = fh.read()
    file_hash = hashlib.md5(data).hexdigest()
    cache_key = f"{abs_path}:{file_hash}"

    if not force_refresh and cache_key in _memory_cache:
        return _memory_cache[cache_key]

    zf = zipfile.ZipFile(BytesIO(data))
    theme_font, theme_colors = _extract_theme(zf)
    scan = _scan_template(zf, theme_colors, theme_font)
    zf.close()

    cache_file = abs_path + ".designspec.json"
    tokens: dict[str, Any] | None = None
    source = "heuristic"

    if not force_refresh and os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as fh:
                disk = json.load(fh)
            if disk.get("hash") == file_hash and isinstance(disk.get("tokens"), dict):
                tokens = disk["tokens"]
                source = disk.get("source", "cached")
                print(f"[design-spec] reusing cached design tokens ({cache_file})")
        except (OSError, json.JSONDecodeError):
            tokens = None

    if tokens is None:
        ai_json = _ask_azure_for_tokens(scan["tokens"], deployment)
        tokens = _merge_ai(scan["tokens"], ai_json)
        source = "ai" if ai_json else "heuristic"
        print(f"[design-spec] design tokens resolved via {source}: {tokens}")
        try:
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump({"hash": file_hash, "tokens": tokens, "source": source}, fh, indent=2)
        except OSError:
            pass

    spec = DesignSpec(
        heading_fill=tokens["heading_fill"],
        heading_text_color=tokens["heading_text_color"],
        heading_font=tokens.get("heading_font"),
        option_fill=tokens["option_fill"],
        option_text_color=tokens["option_text_color"],
        option_font=tokens.get("option_font"),
        table_header_fill=tokens["table_header_fill"],
        table_border_color=tokens["table_border_color"],
        table_header_text_color=tokens["table_header_text_color"],
        table_body_text_color=tokens["table_body_text_color"],
        body_text_color=tokens.get("body_text_color", tokens["heading_text_color"]),
        accent=tokens["accent"],
        source=source,
        heading_pill_el=scan["heading_pill_el"],
        heading_label_el=scan["heading_label_el"],
        option_pill_standalone_el=scan["option_pill_standalone_el"],
        option_label_standalone_el=scan["option_label_standalone_el"],
        option_pill_group_el=scan["option_pill_group_el"],
        logo_el=scan["logo_el"],
        logo_off=scan["logo_off"],
        logo_ext=scan["logo_ext"],
        logo_image_bytes=scan["logo_image_bytes"],
        logo_image_ext=scan["logo_image_ext"],
        title_banner_el=scan["title_banner_el"],
        title_label_el=scan["title_label_el"],
        title_icon_el=scan["title_icon_el"],
        title_icon_off=scan["title_icon_off"],
        title_icon_ext=scan["title_icon_ext"],
        title_icon_image_bytes=scan["title_icon_image_bytes"],
        title_icon_image_ext=scan["title_icon_image_ext"],
    )
    _memory_cache[cache_key] = spec
    return spec
