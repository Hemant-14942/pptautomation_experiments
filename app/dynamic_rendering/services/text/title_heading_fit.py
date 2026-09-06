"""
Auto-fit wide title banner width/font for long heading text.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.dynamic_rendering.constants.shape_geometry import (
    EMU_PER_PT,
    TITLE_HEADING_AVG_CHAR_WIDTH_EM,
    TITLE_HEADING_DEFAULT_FONT_PT,
    TITLE_HEADING_MIN_FONT_SCALE,
    TITLE_HEADING_RIGHT_MARGIN_FRACTION,
    TITLE_HEADING_RIGHT_PADDING_FRACTION,
)


@dataclass(frozen=True)
class HeadingFitResult:
    banner_ext: tuple[int, int]
    label_ext: tuple[int, int]
    label_font_size_pt: float | None
    wrap_mode: bool = False


def estimate_text_width_emu(text: str, font_size_pt: float) -> int:
    return int(len(text) * TITLE_HEADING_AVG_CHAR_WIDTH_EM * font_size_pt * EMU_PER_PT)


def fit_title_heading(
    *,
    text: str,
    banner_off: tuple[int, int],
    banner_ext: tuple[int, int],
    label_off: tuple[int, int],
    label_ext: tuple[int, int],
    baseline_font_size_pt: float | None,
    slide_width: int,
) -> HeadingFitResult:
    text = text or ""
    baseline_pt = baseline_font_size_pt or TITLE_HEADING_DEFAULT_FONT_PT

    text_left_inset = max(0, label_off[0] - banner_off[0])
    right_padding_emu = int(slide_width * TITLE_HEADING_RIGHT_PADDING_FRACTION)
    max_right_edge = int(slide_width * (1 - TITLE_HEADING_RIGHT_MARGIN_FRACTION))
    max_banner_cx = max(max_right_edge - banner_off[0], banner_ext[0])

    required_text_width_emu = estimate_text_width_emu(text, baseline_pt)
    target_banner_cx = text_left_inset + required_text_width_emu + right_padding_emu

    final_banner_cx = min(max(target_banner_cx, banner_ext[0]), max_banner_cx)

    min_label_cx = label_ext[0] if label_ext else 0
    final_label_cx = max(final_banner_cx - text_left_inset - right_padding_emu, min_label_cx)

    label_font_size_pt: float | None = None
    wrap_mode = False
    if target_banner_cx > max_banner_cx and required_text_width_emu > 0:
        scale = final_label_cx / required_text_width_emu
        floor = TITLE_HEADING_MIN_FONT_SCALE * baseline_pt
        shrunk = max(floor, min(baseline_pt * scale, baseline_pt))
        if shrunk < baseline_pt:
            label_font_size_pt = shrunk
            required_at_floor = estimate_text_width_emu(text, floor)
            if required_at_floor > final_label_cx:
                wrap_mode = True

    return HeadingFitResult(
        banner_ext=(final_banner_cx, banner_ext[1]),
        label_ext=(final_label_cx, (label_ext[1] if label_ext else banner_ext[1])),
        label_font_size_pt=label_font_size_pt,
        wrap_mode=wrap_mode,
    )
