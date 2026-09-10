"""Fixed layout for question pill + question text only (no table, no MCQ)."""

INCH_EMU = 914_400
SLIDE_HEIGHT_EMU = 22.5 * INCH_EMU

CONTENT_LEFT_EMU = 1_104_806
CONTENT_WIDTH_EMU = 34_747_200
PILL_TO_TEXT_GAP_EMU = 145_275

QUESTION_PILL = {
    "x": -1_864_528,
    "y": 681_774,
    "width": 7_081_988,
    "height": 1_569_660,
}

QUESTION_LABEL = {
    "x": 1_039_500,
    "y": 827_049,
    "width": 4_562_190,
    "height": 1_015_622,
}

QUESTION_TEXT = {
    "x": CONTENT_LEFT_EMU,
    "y": QUESTION_PILL["y"] + QUESTION_PILL["height"] + PILL_TO_TEXT_GAP_EMU,
    "width": CONTENT_WIDTH_EMU,
    "height": int(0.6 * SLIDE_HEIGHT_EMU),
}
