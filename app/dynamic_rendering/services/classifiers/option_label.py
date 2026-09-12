"""Shared MCQ option pill label parsing and shape lookup."""

from __future__ import annotations

import re

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import OPTION_CX, OPTION_CY
from app.dynamic_rendering.utils.xml.helpers import in_range, local_name, off_ext, prst_geom, text_of

_OPTION_LABEL_RE = re.compile(
    r"^(?:[A-Fa-f]|[1-6]|i{1,3}|iv|v|vi|I{1,3}|IV|V|VI)$"
)
_INPUT_OPTION_LABEL_RE = re.compile(r"^[A-Z]$")
_OPTION_PILL_GEOMS = frozenset({"ellipse", "roundRect", "round2SameRect"})
_MAX_TEMPLATE_OPTION_LABELS = 6
_ROMAN_LOWER = ("i", "ii", "iii", "iv", "v", "vi")
_ROMAN_UPPER = ("I", "II", "III", "IV", "V", "VI")


def parse_input_option_label(text: str) -> str | None:
    """Return capital letter A–Z for blue input deck option labels."""
    key = (text or "").strip()
    if not key or not _INPUT_OPTION_LABEL_RE.match(key):
        return None
    return key


def parse_option_label(text: str) -> str | None:
    """Return normalized option key if text is A-F, 1-6, or roman i-vi."""
    key = (text or "").strip()
    if not key or not _OPTION_LABEL_RE.match(key):
        return None
    return key


def detect_template_label_pattern(sample: str) -> str:
    """Infer label style from one template option label (up to 6 slots)."""
    key = (sample or "").strip()
    if not key:
        return "upper_alpha"
    if re.match(r"^[a-f]$", key):
        return "lower_alpha"
    if re.match(r"^[A-F]$", key):
        return "upper_alpha"
    if re.match(r"^[1-6]$", key):
        return "numeric"
    if key in _ROMAN_LOWER:
        return "roman_lower"
    if key in _ROMAN_UPPER:
        return "roman_upper"
    if key.islower() and key.isalpha() and len(key) == 1:
        return "lower_alpha"
    if key.isdigit():
        return "numeric"
    return "upper_alpha"


def build_template_option_labels(pattern: str, count: int = _MAX_TEMPLATE_OPTION_LABELS) -> list[str]:
    """Build labels for slots 1..count following the template pattern."""
    count = min(count, _MAX_TEMPLATE_OPTION_LABELS)
    if pattern == "lower_alpha":
        return [chr(ord("a") + i) for i in range(count)]
    if pattern == "upper_alpha":
        return [chr(ord("A") + i) for i in range(count)]
    if pattern == "numeric":
        return [str(i + 1) for i in range(count)]
    if pattern == "roman_lower":
        return list(_ROMAN_LOWER[:count])
    if pattern == "roman_upper":
        return list(_ROMAN_UPPER[:count])
    return [chr(ord("A") + i) for i in range(count)]


def option_labels_from_template_samples(samples: list[str]) -> list[str]:
    """Detect pattern from template samples and return 6 labels in that style."""
    for sample in samples:
        if (sample or "").strip():
            pattern = detect_template_label_pattern(sample)
            return build_template_option_labels(pattern)
    return build_template_option_labels("upper_alpha")


def is_input_option_ellipse_el(sp: etree._Element) -> bool:
    if prst_geom(sp) != "ellipse":
        return False
    _, ext = off_ext(sp, "p:spPr")
    return in_range(ext, OPTION_CX, OPTION_CY)


def find_input_option_label_el(
    inner_sps: list[etree._Element],
    pill_el: etree._Element | None = None,
) -> etree._Element | None:
    for sp in inner_sps:
        if sp is pill_el:
            continue
        if local_name(sp) != "sp":
            continue
        if parse_input_option_label(text_of(sp) or "") is not None:
            return sp
    return None


def find_input_option_ellipse_el(inner_sps: list[etree._Element]) -> etree._Element | None:
    for sp in inner_sps:
        if is_input_option_ellipse_el(sp):
            return sp
    return None


def is_input_option_group_el(grp: etree._Element) -> bool:
    if local_name(grp) != "grpSp":
        return False
    inner_sps = [c for c in grp if local_name(c) == "sp"]
    pill_el = find_input_option_ellipse_el(inner_sps)
    if pill_el is None:
        return False
    return find_input_option_label_el(inner_sps, pill_el) is not None


def option_idx_for_letter(letter: str) -> int:
    return ord(letter.upper()) - ord("A")


def find_option_pill_el(inner_sps: list[etree._Element]) -> etree._Element | None:
    for sp in inner_sps:
        geom = prst_geom(sp)
        if geom not in _OPTION_PILL_GEOMS:
            continue
        _, ext = off_ext(sp, "p:spPr")
        if in_range(ext, OPTION_CX, OPTION_CY):
            return sp
    return None


def find_option_label_el(
    inner_sps: list[etree._Element],
    pill_el: etree._Element | None,
) -> etree._Element | None:
    for sp in inner_sps:
        if sp is pill_el:
            continue
        if local_name(sp) != "sp":
            continue
        if parse_option_label(text_of(sp) or "") is not None:
            return sp
    return None
