"""Build DesignSpec from scanned tokens + cloneable XML fragments."""

from __future__ import annotations

from typing import Any

from app.dynamic_rendering.domain.models.design_spec import DesignSpec


def spec_from_tokens_and_scan(tokens: dict[str, Any], source: str, scan: dict[str, Any]) -> DesignSpec:
    """Merge color/font tokens with cloned shape elements from template scan."""
    return DesignSpec(
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
        body_font=tokens.get("body_font"),
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
        question_icon_el=scan["question_icon_el"],
        question_icon_off=scan["question_icon_off"],
        question_icon_ext=scan["question_icon_ext"],
        question_icon_image_bytes=scan["question_icon_image_bytes"],
        question_icon_image_ext=scan["question_icon_image_ext"],
        title_banner_el=scan["title_banner_el"],
        title_label_el=scan["title_label_el"],
        title_icon_el=scan["title_icon_el"],
        title_icon_off=scan["title_icon_off"],
        title_icon_ext=scan["title_icon_ext"],
        title_icon_image_bytes=scan["title_icon_image_bytes"],
        title_icon_image_ext=scan["title_icon_image_ext"],
        title_heading_font_size_pt=scan["title_heading_font_size_pt"],
    )
