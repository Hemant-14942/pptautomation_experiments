"""Build DesignSpec from scanned color tokens + cloneable XML fragments."""

from __future__ import annotations

from typing import Any

from app.dynamic_rendering.constants.template_design import FIXED_FONT, FIXED_HEADING_FONT_PT
from app.dynamic_rendering.domain.models.design_spec import DesignSpec


def spec_from_tokens_and_scan(tokens: dict[str, Any], source: str, scan: dict[str, Any]) -> DesignSpec:
    """Merge template colors/shapes with fixed typography constants."""
    return DesignSpec(
        question_pill_fill=tokens["question_pill_fill"],
        question_pill_text_color=tokens["question_pill_text_color"],
        question_pill_font=FIXED_FONT,
        option_fill=tokens["option_fill"],
        option_text_color=tokens["option_text_color"],
        option_font=FIXED_FONT,
        table_header_fill=tokens["table_header_fill"],
        table_border_color=tokens["table_border_color"],
        table_header_text_color=tokens["table_header_text_color"],
        table_body_text_color=tokens["table_body_text_color"],
        body_text_color=tokens.get("body_text_color", tokens["question_pill_text_color"]),
        body_font=FIXED_FONT,
        accent=tokens["accent"],
        source=source,
        question_pill_el=scan["question_pill_el"],
        question_pill_label_el=scan["question_pill_label_el"],
        option_pill_standalone_el=scan["option_pill_standalone_el"],
        option_label_standalone_el=scan["option_label_standalone_el"],
        option_pill_group_el=scan["option_pill_group_el"],
        title_banner_el=scan["title_banner_el"],
        title_label_el=scan["title_label_el"],
        title_icon_el=scan["title_icon_el"],
        title_icon_off=scan["title_icon_off"],
        title_icon_ext=scan["title_icon_ext"],
        title_icon_image_bytes=scan["title_icon_image_bytes"],
        title_icon_image_ext=scan["title_icon_image_ext"],
        title_heading_font_size_pt=FIXED_HEADING_FONT_PT,
    )
