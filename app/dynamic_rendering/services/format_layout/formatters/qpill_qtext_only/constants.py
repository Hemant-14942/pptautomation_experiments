"""Fixed layout for question pill + question text only (no table, no MCQ)."""

from app.dynamic_rendering.services.format_layout.shared.qpill_layout import (
    QUESTION_PILL,
    question_pill_for,
)

INCH_EMU = 914_400
SLIDE_HEIGHT_EMU = int(22.5 * INCH_EMU)

CONTENT_LEFT_EMU = 1_104_806
CONTENT_WIDTH_EMU = 34_747_200
PILL_TO_TEXT_GAP_EMU = 220_000
QUESTION_TEXT = {
    "x": CONTENT_LEFT_EMU,
    "y": QUESTION_PILL["y"] + QUESTION_PILL["height"] + PILL_TO_TEXT_GAP_EMU,
    "width": CONTENT_WIDTH_EMU,
    "height": int(0.6 * SLIDE_HEIGHT_EMU),
}


def question_text_for(dspec=None) -> dict:
    pill = question_pill_for(dspec)
    y = pill["y"] + pill["height"] + PILL_TO_TEXT_GAP_EMU
    return {
        "x": CONTENT_LEFT_EMU,
        "y": y,
        "width": CONTENT_WIDTH_EMU,
        "height": QUESTION_TEXT["height"],
    }
