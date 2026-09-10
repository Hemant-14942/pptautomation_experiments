"""Fixed layout for question pill + text + image + MCQ slides."""

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
    MCQ_OPTIONS as _BASE_MCQ_OPTIONS,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 40 * INCH_EMU
HALF_SLIDE_EMU = SLIDE_WIDTH_EMU // 2
COLUMN_GAP_EMU = int(0.2 * INCH_EMU)
CONTENT_LEFT_EMU = 1_104_806
ANSWER_TEXT_X = 3_107_605
LEFT_ANSWER_WIDTH_EMU = HALF_SLIDE_EMU - ANSWER_TEXT_X - COLUMN_GAP_EMU

MCQ_OPTIONS = []
for opt in _BASE_MCQ_OPTIONS:
    text_box = dict(opt["text_box"])
    text_box["width"] = LEFT_ANSWER_WIDTH_EMU
    MCQ_OPTIONS.append({**opt, "text_box": text_box})

_MCQ_ZONE_TOP = _BASE_MCQ_OPTIONS[0]["pill"]["y"]
_LAST_PILL = _BASE_MCQ_OPTIONS[3]["pill"]
_MCQ_ZONE_BOTTOM = _LAST_PILL["y"] + _LAST_PILL["height"]

IMAGE_BOX = {
    "x": HALF_SLIDE_EMU + COLUMN_GAP_EMU,
    "y": _MCQ_ZONE_TOP,
    "width": SLIDE_WIDTH_EMU - (HALF_SLIDE_EMU + COLUMN_GAP_EMU) - CONTENT_LEFT_EMU,
    "height": _MCQ_ZONE_BOTTOM - _MCQ_ZONE_TOP + int(0.5 * INCH_EMU),
}
