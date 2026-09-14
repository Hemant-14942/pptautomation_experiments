"""Layout slots for MCQ options A–D and extrapolated rows beyond D."""

from __future__ import annotations

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
    mcq_options_for,
)


def option_layout_from_options(option_idx: int, options: list[dict]) -> dict:
    """Return pill, label_box, text_box, and label letter from a constants MCQ_OPTIONS list."""
    if not options:
        raise ValueError("options must not be empty")

    row_gap = options[1]["pill"]["y"] - options[0]["pill"]["y"]
    text_row_gap = options[1]["text_box"]["y"] - options[0]["text_box"]["y"]
    first_label_box = options[0].get("label_box")
    label_x = first_label_box["x"] if first_label_box else options[0]["pill"]["x"]
    label_width = first_label_box["width"] if first_label_box else options[0]["pill"]["width"]
    label_height = first_label_box["height"] if first_label_box else options[0]["pill"]["height"]
    label_y_offset = (
        first_label_box["y"] - options[0]["pill"]["y"] if first_label_box else 0
    )

    def _label_box_for_pill_y(pill_y: int) -> dict[str, int]:
        return {
            "x": label_x,
            "y": pill_y + label_y_offset,
            "width": label_width,
            "height": label_height,
        }

    if option_idx < len(options):
        opt = dict(options[option_idx])
        if opt.get("label_box") is None:
            opt["label_box"] = _label_box_for_pill_y(opt["pill"]["y"])
        return opt

    base = options[3]
    extra = option_idx - 3
    pill_y = base["pill"]["y"] + extra * row_gap
    text_y = base["text_box"]["y"] + extra * text_row_gap
    pill = {**base["pill"], "y": pill_y}
    text_box = {**base["text_box"], "y": text_y}
    letter = chr(ord("A") + option_idx)
    return {
        "label": letter,
        "pill": pill,
        "label_box": _label_box_for_pill_y(pill_y),
        "text_box": text_box,
    }


def option_layout_for(option_idx: int, dspec=None) -> dict:
    """Return layout for qpill_qtext_mcq option rows (defence-aware)."""
    return option_layout_from_options(option_idx, mcq_options_for(dspec))
