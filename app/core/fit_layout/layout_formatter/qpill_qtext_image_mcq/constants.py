"""Fixed layout for question pill + text + image + MCQ slides.

Reference: app/data/input/ptest1.pptx slide 16 (index 15).

Layout (top to bottom):
  ROW 1 — question pill + question text (full width with margins, same as qpill_qtext_mcq)
  ROW 2 — split 50/50 below question text:
    LEFT 50%  — MCQ pills + answer text (wrap + normAutofit)
    RIGHT 50% — image box (aspect ratio kept, no overlap with row 1)

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches).
"""

from app.core.fit_layout.layout_formatter.qpill_qtext_mcq.constants import (
    MCQ_OPTIONS as _BASE_MCQ_OPTIONS,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 40 * INCH_EMU
HALF_SLIDE_EMU = SLIDE_WIDTH_EMU // 2          # 20 inches
COLUMN_GAP_EMU = int(0.2 * INCH_EMU)           # gap at center divider
CONTENT_LEFT_EMU = 1_104_806                   # 1.208 inches (right margin matches)

ANSWER_TEXT_X = 3_107_605                      # same left edge as qpill_qtext_mcq answers

# Answer text stays in LEFT 50% only (does not extend under image)
LEFT_ANSWER_WIDTH_EMU = HALF_SLIDE_EMU - ANSWER_TEXT_X - COLUMN_GAP_EMU

# MCQ pills: same y positions as qpill_qtext_mcq; answer boxes narrowed to left half
MCQ_OPTIONS = []
for opt in _BASE_MCQ_OPTIONS:
    text_box = dict(opt["text_box"])
    text_box["width"] = LEFT_ANSWER_WIDTH_EMU
    MCQ_OPTIONS.append({**opt, "text_box": text_box})

# Image box: RIGHT 50%, vertically aligned with MCQ zone (starts at option A, not at question text)
_MCQ_ZONE_TOP = _BASE_MCQ_OPTIONS[0]["pill"]["y"]
_LAST_PILL = _BASE_MCQ_OPTIONS[3]["pill"]
_MCQ_ZONE_BOTTOM = _LAST_PILL["y"] + _LAST_PILL["height"]

IMAGE_BOX = {
    "x": HALF_SLIDE_EMU + COLUMN_GAP_EMU,
    "y": _MCQ_ZONE_TOP,
    "width": SLIDE_WIDTH_EMU - (HALF_SLIDE_EMU + COLUMN_GAP_EMU) - CONTENT_LEFT_EMU,
    "height": _MCQ_ZONE_BOTTOM - _MCQ_ZONE_TOP + int(0.5 * INCH_EMU),
}
