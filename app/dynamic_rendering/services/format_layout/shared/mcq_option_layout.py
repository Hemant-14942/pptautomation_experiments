"""Layout slots for MCQ options A–D and extrapolated rows beyond D."""

from __future__ import annotations

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
    MCQ_OPTIONS,
    OPTION_A_LABEL,
)

ROW_GAP = MCQ_OPTIONS[1]["pill"]["y"] - MCQ_OPTIONS[0]["pill"]["y"]
TEXT_ROW_GAP = MCQ_OPTIONS[1]["text_box"]["y"] - MCQ_OPTIONS[0]["text_box"]["y"]
_LABEL_Y_OFFSET = OPTION_A_LABEL["y"] - MCQ_OPTIONS[0]["pill"]["y"]
_LABEL_X = OPTION_A_LABEL["x"]
_LABEL_WIDTH = OPTION_A_LABEL["width"]
_LABEL_HEIGHT = OPTION_A_LABEL["height"]


def _label_box_for_pill_y(pill_y: int) -> dict[str, int]:
    return {
        "x": _LABEL_X,
        "y": pill_y + _LABEL_Y_OFFSET,
        "width": _LABEL_WIDTH,
        "height": _LABEL_HEIGHT,
    }


def option_layout_for(option_idx: int) -> dict:
    """Return pill, label_box, text_box, and label letter for a layout row index."""
    if option_idx < len(MCQ_OPTIONS):
        opt = dict(MCQ_OPTIONS[option_idx])
        if opt.get("label_box") is None:
            opt["label_box"] = _label_box_for_pill_y(opt["pill"]["y"])
        return opt

    base = MCQ_OPTIONS[3]
    extra = option_idx - 3
    pill_y = base["pill"]["y"] + extra * ROW_GAP
    text_y = base["text_box"]["y"] + extra * TEXT_ROW_GAP
    pill = {**base["pill"], "y": pill_y}
    text_box = {**base["text_box"], "y": text_y}
    letter = chr(ord("A") + option_idx)
    return {
        "label": letter,
        "pill": pill,
        "label_box": _label_box_for_pill_y(pill_y),
        "text_box": text_box,
    }
