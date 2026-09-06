"""
One template slide's layout summary (from parse_template in Session 4).

Used for slide matching: "input slide with table → use template slide 4".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ShapeStyle:
    """Lightweight summary of one shape on a template slide (not full XML)."""

    name: str
    shape_type: str              # "sp", "pic", "grpSp", "graphicFrame"
    left: int | None             # x in EMU
    top: int | None              # y in EMU
    width: int | None            # cx in EMU
    height: int | None           # cy in EMU
    has_text: bool
    sample_text: str             # first ~80 chars of text, for heuristics
    fill_hex: str | None
    font_name: str | None
    font_size_pt: int | None
    font_color_hex: str | None
    is_group: bool = False
    is_table: bool = False
    is_picture: bool = False

    @property
    def role(self) -> str:
        """
        Guess shape role from name, text, and size — for slide matching.

        Returns labels like: question_badge, option_pill, table, body, picture.
        """
        n = self.name.lower() + " " + self.sample_text.lower()
        if "question" in n:
            return "question_badge"
        if self.is_picture:
            return "picture"
        if self.is_table:
            return "table"
        if self.is_group and self.width and self.height and self.width < 2000000:
            return "option_pill"
        if self.is_group:
            return "decorative_group"
        if self.has_text and self.width and self.width > 30000000 and self.height and self.height < 1500000:
            return "heading"
        if self.has_text and self.sample_text:
            return "body"
        return "decoration"


@dataclass
class SlideDesign:
    """Everything we know about one slide in the template .pptx."""

    index: int                           # 0-based slide index
    layout_name: str                     # e.g. "Title Slide", "Blank"
    background_xml: bytes | None         # raw p:bg XML to clone onto output
    background_kind: str                 # "image" | "solid" | "none" | "other"
    theme_font: str | None               # major theme font from theme1.xml
    theme_colors: dict[str, str] = field(default_factory=dict)
    shapes: list[ShapeStyle] = field(default_factory=list)

    @property
    def fingerprint(self) -> dict[str, Any]:
        """
        Small summary dict for matching input slides to template slides.

        Example: table_count=1, has_question_badge=True, option_pills=4.
        """
        return {
            "layout": self.layout_name,
            "shape_count": len(self.shapes),
            "text_count": sum(1 for s in self.shapes if s.has_text),
            "group_count": sum(1 for s in self.shapes if s.is_group),
            "table_count": sum(1 for s in self.shapes if s.is_table),
            "picture_count": sum(1 for s in self.shapes if s.is_picture),
            "option_pills": sum(1 for s in self.shapes if s.role == "option_pill"),
            "has_question_badge": any(s.role == "question_badge" for s in self.shapes),
            "has_heading": any(s.role == "heading" for s in self.shapes),
            "has_body": any(s.role == "body" for s in self.shapes),
            "has_decorative_group": any(s.role == "decorative_group" for s in self.shapes),
        }