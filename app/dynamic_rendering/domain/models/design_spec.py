"""
Template design recipe — colors, fonts, and cloneable shape XML.

Built once per template by design_spec service (Session 5).
Used by input_collector and shape_emitters to restyle the input deck.
"""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class DesignSpec:
    # --- Color / font tokens (hex without #, e.g. "015500") -----------------

    heading_fill: str              # MCQ question pill + table header background
    heading_text_color: str      # text on question pill / table header
    heading_font: str | None     # font for question pill label (often Cambria)

    option_fill: dict[str, str]  # letter → color, e.g. {"A": "FF0000", "B": "0000FF"}
    option_text_color: str       # text color on A/B/C/D labels
    option_font: str | None      # font for option letters

    table_header_fill: str       # fallback; often same as heading_fill
    table_border_color: str
    table_header_text_color: str
    table_body_text_color: str

    body_text_color: str         # normal paragraph text on slide
    body_font: str | None        # normal body font (design team: Cambria)

    accent: str                  # last-resort color if option letter missing
    source: str = "heuristic"    # where tokens came from: heuristic / cached

    # --- Cloneable MCQ "Question" pill shapes from template XML ------------
    # XML: p:sp roundRect + optional label p:sp beside it

    heading_pill_el: etree._Element | None = None   # green rounded rectangle
    heading_label_el: etree._Element | None = None  # "Question" text shape

    # --- Cloneable option pills (standalone circle + label, or grpSp) ----

    option_pill_standalone_el: etree._Element | None = None
    option_label_standalone_el: etree._Element | None = None
    option_pill_group_el: etree._Element | None = None  # pill+label inside grpSp

    # --- Logo (usually bottom-right picture) -------------------------------

    logo_el: etree._Element | None = None           # p:pic XML to clone
    logo_off: tuple[int, int] | None = None         # (x, y) position in EMU
    logo_ext: tuple[int, int] | None = None         # (width, height) in EMU
    logo_image_bytes: bytes | None = None           # raw PNG/JPG bytes
    logo_image_ext: str | None = None               # "png", "jpg", etc.

    # --- Question icon (small image overlapping question pill) -------------

    question_icon_el: etree._Element | None = None
    question_icon_off: tuple[int, int] | None = None
    question_icon_ext: tuple[int, int] | None = None
    question_icon_image_bytes: bytes | None = None
    question_icon_image_ext: str | None = None

    # --- Topic title banner (wide bar + corner icon on last template slide) -

    title_banner_el: etree._Element | None = None   # wide roundRect bar
    title_label_el: etree._Element | None = None    # separate text shape, if any
    title_icon_el: etree._Element | None = None     # icon left of banner
    title_icon_off: tuple[int, int] | None = None
    title_icon_ext: tuple[int, int] | None = None
    title_icon_image_bytes: bytes | None = None
    title_icon_image_ext: str | None = None
    title_heading_font_size_pt: float | None = None # template's authored title size

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