from __future__ import annotations

from dataclasses import dataclass

from app.constants.shape_geometry import (
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
    # None => leave the template's own baseline font size untouched
    # (either it already fit, or there's no text to measure).
    label_font_size_pt: float | None
    # True => text overflowed even at font floor; enable wrapping instead.
    wrap_mode: bool = False


def estimate_text_width_emu(text: str, font_size_pt: float) -> int:
    """Char-count x average-glyph-advance heuristic -- NOT real glyph
    metrics. TITLE_HEADING_AVG_CHAR_WIDTH_EM is a tunable approximation of
    a proportional sans/serif's average advance width as a fraction of
    its em (point) size."""
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
    """Widen the banner/label rightward -- up to the master layout's
    right-margin boundary -- to fit `text` on one line at the template's
    own baseline font size. Only shrinks the font (down to a floor) if
    even the max-width pill can't fit it. Never wraps, never moves the
    icon, never touches the left/top edges or the banner/label height."""
    text = text or ""
    baseline_pt = baseline_font_size_pt or TITLE_HEADING_DEFAULT_FONT_PT

    text_left_inset = max(0, label_off[0] - banner_off[0])
    right_padding_emu = int(slide_width * TITLE_HEADING_RIGHT_PADDING_FRACTION)
    max_right_edge = int(slide_width * (1 - TITLE_HEADING_RIGHT_MARGIN_FRACTION))
    # Never shrink below the template's/input's own original width, even if
    # that means slightly exceeding the margin on a pathological template.
    max_banner_cx = max(max_right_edge - banner_off[0], banner_ext[0])

    required_text_width_emu = estimate_text_width_emu(text, baseline_pt)
    target_banner_cx = text_left_inset + required_text_width_emu + right_padding_emu

    final_banner_cx = min(max(target_banner_cx, banner_ext[0]), max_banner_cx)

    min_label_cx = label_ext[0] if label_ext else 0
    final_label_cx = max(final_banner_cx - text_left_inset - right_padding_emu, min_label_cx)

    label_font_size_pt: float | None = None
    wrap_mode = False
    if target_banner_cx > max_banner_cx and required_text_width_emu > 0:
        # required_text_width_emu is linear in font_size_pt, so this scale
        # is exact (not iterative): the font size that makes the estimated
        # width equal final_label_cx.
        scale = final_label_cx / required_text_width_emu
        floor = TITLE_HEADING_MIN_FONT_SCALE * baseline_pt
        shrunk = max(floor, min(baseline_pt * scale, baseline_pt))
        if shrunk < baseline_pt:
            label_font_size_pt = shrunk
            # Check if text still overflows even at floor size
            required_at_floor = estimate_text_width_emu(text, floor)
            if required_at_floor > final_label_cx:
                wrap_mode = True

    return HeadingFitResult(
        banner_ext=(final_banner_cx, banner_ext[1]),
        label_ext=(final_label_cx, (label_ext[1] if label_ext else banner_ext[1])),
        label_font_size_pt=label_font_size_pt,
        wrap_mode=wrap_mode,
    )
