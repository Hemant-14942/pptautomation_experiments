"""
Detect slide title text on input decks (design team: 80pt Cambria heading).
"""

from __future__ import annotations

from typing import Any

from app.dynamic_rendering.constants.design_tokens_defaults import DEFAULT_HEADING_FONT_PT
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, q


def extract_color_from_run(run_element) -> str | None:
    rPr = run_element.find(q("a:rPr"))
    if rPr is None:
        return None
    solidFill = rPr.find(q("a:solidFill"))
    if solidFill is None:
        return None
    srgb = solidFill.find(q("a:srgbClr"))
    if srgb is not None:
        hex_val = srgb.get("val")
        if hex_val:
            return "#" + hex_val
    return None


def get_text_run_info(run_element, shape_position) -> dict[str, Any] | None:
    t_elem = run_element.find(q("a:t"))
    if t_elem is None or not t_elem.text:
        return None
    text = t_elem.text.strip()
    if not text:
        return None

    rPr = run_element.find(q("a:rPr"))
    info: dict[str, Any] = {
        "text": text,
        "font_size_pt": None,
        "bold": False,
        "font_name": None,
        "color": None,
        "italic": False,
        "underline": False,
        "position_top_left": shape_position,
        "position_center": None,
    }

    if rPr is not None:
        sz = rPr.get("sz")
        if sz:
            try:
                info["font_size_pt"] = int(int(sz) / 100)
            except ValueError:
                pass
        b = rPr.get("b")
        info["bold"] = b == "1" or b == "true"
        i = rPr.get("i")
        info["italic"] = i == "1" or i == "true"
        u = rPr.get("u")
        info["underline"] = bool(u and u != "none")
        latin = rPr.find(q("a:latin"))
        if latin is not None:
            info["font_name"] = latin.get("typeface")
        info["color"] = extract_color_from_run(run_element)

    if shape_position and shape_position[0] is not None:
        info["position_center"] = shape_position
    return info


def pick_heading(text_elements: list[dict[str, Any]], slide_height: int) -> dict[str, Any] | None:
    if not text_elements:
        return None

    size_80 = [e for e in text_elements if e.get("font_size_pt") == DEFAULT_HEADING_FONT_PT]
    if not size_80:
        return None

    def sort_key(e):
        pos = e.get("position_top_left") or (0, 10**12)
        y = pos[1] if len(pos) > 1 else 10**12
        x = pos[0] if pos else 0
        return (y, x, 0 if e.get("bold") else 1)

    pool = sorted(size_80, key=sort_key)
    first = pool[0]
    pos = first.get("position_top_left")
    same_shape = [e for e in pool if e.get("position_top_left") == pos]
    text = "".join(e["text"] for e in same_shape)

    return {
        "text": text,
        "font_size_pt": first.get("font_size_pt"),
        "bold": first.get("bold"),
        "font_name": first.get("font_name"),
        "color": first.get("color"),
        "italic": first.get("italic"),
        "underline": first.get("underline"),
        "position_top_left": first.get("position_top_left"),
        "position_center": first.get("position_center"),
        "shape_size": first.get("shape_size"),
        "used_size_80": bool(size_80),
        "run_count": len(same_shape),
    }


def extract_text_from_slide(slide, slide_number: int, prs) -> dict[str, Any]:
    sptree = slide._element.find(q("p:cSld") + "/" + q("p:spTree"))
    if sptree is None:
        return {"slide_number": slide_number, "heading": None}

    children = [c for c in list(sptree) if local_name(c) == "sp"]
    text_elements: list[dict[str, Any]] = []

    for child in children:
        off, ext = off_ext(child, "p:spPr")
        txBody = child.find(q("p:txBody"))
        if txBody is None:
            continue
        for para in txBody.iter(q("a:p")):
            for run in para.iter(q("a:r")):
                text_info = get_text_run_info(run, off)
                if text_info:
                    text_info["shape_size"] = ext
                    text_elements.append(text_info)

    heading = pick_heading(text_elements, int(prs.slide_height))
    return {
        "slide_number": slide_number,
        "slide_width": int(prs.slide_width),
        "slide_height": int(prs.slide_height),
        "heading": heading,
    }
