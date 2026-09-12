"""
Template design recipe — colors, fonts, and cloneable shape XML.

Built once per template by design_spec service (Session 5).
Used by input_collector and shape_emitters to restyle the input deck.
"""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from app.dynamic_rendering.constants.template_design import FIXED_FONT, FIXED_HEADING_FONT_PT
from app.dynamic_rendering.services.classifiers.option_label import option_idx_for_letter


@dataclass
class DesignSpec:
    # --- Color / font tokens (hex without #, e.g. "015500") -----------------

    question_pill_fill: str              # MCQ question pill + table header background
    question_pill_text_color: str        # text on question pill / table header
    option_fill: dict[str, str]          # letter → color, e.g. {"A": "FF0000"}
    option_labels: list[str]             # template label text for slots A..F (6 max)
    option_text_color: str               # text color on A/B/C/D labels
    table_header_fill: str               # fallback; often same as question_pill_fill
    table_border_color: str
    table_header_text_color: str
    table_body_text_color: str
    body_text_color: str                 # normal paragraph text on slide
    accent: str                          # last-resort color if option letter missing
    question_pill_font: str = FIXED_FONT
    option_font: str = FIXED_FONT
    body_font: str = FIXED_FONT
    source: str = "heuristic"

    # --- Cloneable MCQ "Question" pill shapes from template XML ------------
    # XML: p:sp roundRect + optional label p:sp beside it

    question_pill_el: etree._Element | None = None   # green rounded rectangle
    question_pill_label_el: etree._Element | None = None  # "Question" text shape

    # --- Cloneable option pills (standalone circle + label, or grpSp) ----

    option_pill_standalone_el: etree._Element | None = None
    option_label_standalone_el: etree._Element | None = None
    option_pill_group_el: etree._Element | None = None  # pill+label inside grpSp

    # --- Topic title banner (wide bar + corner icon on last template slide) -

    title_banner_el: etree._Element | None = None   # wide roundRect bar
    title_label_el: etree._Element | None = None    # separate text shape, if any
    title_icon_el: etree._Element | None = None     # icon left of banner
    title_icon_off: tuple[int, int] | None = None
    title_icon_ext: tuple[int, int] | None = None
    title_icon_image_bytes: bytes | None = None
    title_icon_image_ext: str | None = None
    title_heading_font_size_pt: float = FIXED_HEADING_FONT_PT

    def option_color_for(self, letter: str) -> str:
        """
        Pick fill color for option pill letter A/B/C/D.

        Checks option_fill dict first, then "shared", then accent fallback.
        """
        letter = (letter or "").upper()           # normalize to "A" not "a"
        if letter in self.option_fill:
            return self.option_fill[letter]       # per-letter color from template
        if "shared" in self.option_fill:
            return self.option_fill["shared"]     # one color for all options
        return self.accent                        # last resort

    def option_label_for(self, letter: str, fallback: str = "") -> str:
        """Return template label text for input option letter (A→slot 0, B→slot 1, …)."""
        idx = option_idx_for_letter(letter or "")
        if 0 <= idx < len(self.option_labels):
            return self.option_labels[idx]
        return fallback or letter