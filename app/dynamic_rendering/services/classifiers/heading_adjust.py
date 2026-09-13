"""Shape pairing and layout helpers for input classification."""

from __future__ import annotations

from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import LABEL_PAIRING_TOLERANCE, PILL_CONTENT_GAP
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.format_layout.shared.title_heading_layout import fixed_title_heading_geometry
from app.dynamic_rendering.services.text.heading_detector import extract_text_from_slide
from app.dynamic_rendering.services.text.title_heading_fit import fit_title_heading
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, parse_emu, q, text_of


def find_paired_label(children: list, i: int, off, ext, claimed: set) -> etree._Element | None:
    if i + 1 < len(children):
        nxt = children[i + 1]
        if local_name(nxt) == "sp" and id(nxt) not in claimed:
            claimed.add(id(nxt))
            return nxt
    if not off or not ext:
        return None
    for c in children:
        if id(c) in claimed or local_name(c) != "sp":
            continue
        coff, cext = off_ext(c, "p:spPr")
        if not coff or not cext:
            continue
        if abs(coff[0] - off[0]) < LABEL_PAIRING_TOLERANCE and abs(coff[1] - off[1]) < LABEL_PAIRING_TOLERANCE:
            claimed.add(id(c))
            return c
    return None


def body_matches_heading_box(item: dict[str, Any], hpos) -> bool:
    if item.get("kind") != "body" or item.get("xml") is None or not hpos:
        return False
    off, _ = off_ext(item["xml"], "p:spPr")
    if not off:
        return False
    return int(off[0]) == int(hpos[0]) and int(off[1]) == int(hpos[1])


def item_off_ext(item: dict[str, Any]):
    if item.get("off"):
        return item["off"], item.get("ext")
    xml = item.get("xml")
    if xml is None:
        return None, None
    off, ext = off_ext(xml, "p:spPr")
    if off:
        return off, ext
    off, ext = off_ext(xml, "p:grpSpPr")
    if off:
        return off, ext
    xfrm = xml.find(q("p:xfrm"))
    if xfrm is None:
        return None, None
    off_el = xfrm.find(q("a:off"))
    ext_el = xfrm.find(q("a:ext"))
    off_t = (parse_emu(off_el.get("x")), parse_emu(off_el.get("y"))) if off_el is not None else None
    ext_t = (parse_emu(ext_el.get("cx")), parse_emu(ext_el.get("cy"))) if ext_el is not None else None
    return off_t, ext_t


def nudge_y(item: dict[str, Any], dy: int) -> None:
    if dy <= 0:
        return
    if item.get("off"):
        x, y = item["off"]
        item["off"] = (x, y + dy)
    xml = item.get("xml")
    if xml is None:
        return
    for pref in ("p:spPr", "p:grpSpPr"):
        container = xml.find(q(pref))
        if container is None:
            continue
        xfrm = container.find(q("a:xfrm"))
        if xfrm is None:
            continue
        off_el = xfrm.find(q("a:off"))
        if off_el is not None:
            off_el.set("y", str(parse_emu(off_el.get("y")) + dy))
        return
    xfrm = xml.find(q("p:xfrm"))
    if xfrm is None:
        return
    off_el = xfrm.find(q("a:off"))
    if off_el is not None:
        off_el.set("y", str(parse_emu(off_el.get("y")) + dy))


def shift_content_below_pill(items: list[dict[str, Any]]) -> None:
    pill = next((it for it in items if it.get("kind") == "title_heading"), None)
    if pill is None or not pill.get("off") or not pill.get("ext"):
        return
    target_y = pill["off"][1] + pill["ext"][1] + PILL_CONTENT_GAP
    for it in items:
        if it.get("kind") in {"title_heading", "heading"}:
            continue
        off, _ = item_off_ext(it)
        if not off:
            continue
        if off[1] < target_y:
            nudge_y(it, target_y - off[1])


def apply_detected_heading(
    items: list[dict[str, Any]],
    heading: dict[str, Any] | None,
    dspec: DesignSpec | None,
    slide_width: int,
) -> list[dict[str, Any]]:
    if not heading or not heading.get("text") or dspec is None or dspec.title_banner_el is None:
        return items

    hpos = heading.get("position_top_left")
    items = [it for it in items if not body_matches_heading_box(it, hpos)]

    baseline_pt = dspec.title_heading_font_size_pt

    if not any(it.get("kind") == "title_heading" for it in items):
        geo = fixed_title_heading_geometry()
        banner_off = geo["banner_off"]
        banner_ext = geo["banner_ext"]
        label_off = geo["label_off"]
        label_ext = geo["label_ext"]
        fit = fit_title_heading(
            text=heading["text"],
            banner_off=banner_off,
            banner_ext=banner_ext,
            label_off=label_off,
            label_ext=label_ext,
            baseline_font_size_pt=baseline_pt,
            slide_width=slide_width,
        )
        items.insert(
            0,
            {
                "kind": "title_heading",
                "off": banner_off,
                "ext": fit.banner_ext,
                "label_text": heading["text"],
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
            },
        )
    else:
        for it in items:
            if it.get("kind") != "title_heading":
                continue
            it["label_text"] = heading["text"]
            orig_off = it.get("_orig_off", it["off"])
            orig_ext = it.get("_orig_ext", it["ext"])
            orig_label_off = it.get("_orig_label_off", it["label_off"])
            orig_label_ext = it.get("_orig_label_ext", it["label_ext"])
            fit = fit_title_heading(
                text=heading["text"],
                banner_off=orig_off,
                banner_ext=orig_ext,
                label_off=orig_label_off,
                label_ext=orig_label_ext,
                baseline_font_size_pt=baseline_pt,
                slide_width=slide_width,
            )
            it["ext"] = fit.banner_ext
            it["label_ext"] = fit.label_ext
            it["label_font_size_pt"] = fit.label_font_size_pt
            it["wrap_mode"] = fit.wrap_mode

    shift_content_below_pill(items)
    return items


def detected_heading_for_slide(slide, idx: int, prs):
    return extract_text_from_slide(slide, idx, prs).get("heading")
