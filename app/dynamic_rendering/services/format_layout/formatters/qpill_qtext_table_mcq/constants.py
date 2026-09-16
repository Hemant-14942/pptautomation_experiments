"""Fixed layout for question + text + table + MCQ slides.

Extracted from app/data/input/p.pptx slide 0 (index 0).

Layout order (top to bottom):
  1. Question pill + "Question" label
  2. Question text box (multi-line)
  3. Table (5 rows x 2 cols on reference slide)
  4. Four MCQ options (A, B, C, D) — pill + answer text each

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches).
1 inch = 914,400 EMU.

Gaps on reference slide:
  pill to question text:  ~0.16in
  question text to table: ~0.57in
  table to option A:       ~1.44in
  between MCQ options:     ~0.57in

Option A pill + "A" label are separate shapes (like qpill_qtext_mcq).
Options B, C, D pills are grouped with their labels (<p:grpSp>).
"""

# ============================================================================
# SECTION 1: QUESTION PILL (top, bleeds off left edge)
# ============================================================================

QUESTION_PILL = {
    "x": -1_864_528,     # -2.039 inches
    "y": 681_774,        # 0.746 inches
    "width": 7_081_988,  # 7.745 inches
    "height": 1_569_660, # 1.717 inches
}

QUESTION_LABEL = {
    "x": 1_039_500,      # 1.137 inches
    "y": 827_049,        # 0.904 inches
    "width": 4_562_190,  # 4.989 inches
    "height": 1_015_622, # 1.111 inches
}

# ============================================================================
# SECTION 2: QUESTION TEXT BOX (below pill)
# ============================================================================

PILL_TO_TEXT_GAP_EMU = 220_000

# Text fit order (question + answer boxes):
#   1. wrap="square"  — long lines break to next row (no spill off right edge)
#   2. normAutofit      — if wrapped text still too tall, shrink font to fit
QUESTION_TEXT = {
    "x": 1_104_806,      # 1.208 inches
    "y": QUESTION_PILL["y"] + QUESTION_PILL["height"] + PILL_TO_TEXT_GAP_EMU,
    "width": 34_747_200, # 38.0 inches
    "height": 2_560_320, # 2.8 inches (shorter than qpill_qtext_mcq — table below)
}

# ============================================================================
# SECTION 3: TABLE (below question text)
# ============================================================================

TABLE_BOX = {
    "x": 1_104_806,      # 1.208 inches (same left edge as question text)
    "y": 5_477_256,      # 5.990 inches
    "width": 34_747_200, # 38.0 inches
    "height": 4_575_657, # 5.004 inches (table keeps its own row heights)
}

# ============================================================================
# SECTION 4: MCQ OPTIONS (below table)
# ============================================================================

OPTION_A_PILL = {
    "x": 1_039_499,
    "y": 11_373_307,     # 12.438 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_A_LABEL = {
    "x": 1_104_807,
    "y": 11_571_732,     # 12.655 inches
    "width": 1_466_700,
    "height": 1_169_511,
}

OPTION_A_TEXT = {
    "x": 3_107_605,
    "y": 11_664_086,     # 12.756 inches
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_B_PILL = {
    "x": 1_039_499,
    "y": 13_490_143,     # 14.753 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_B_TEXT = {
    "x": 3_107_605,
    "y": 13_721_486,     # 15.006 inches
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_C_PILL = {
    "x": 1_039_499,
    "y": 15_607_893,     # 17.069 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_C_TEXT = {
    "x": 3_107_605,
    "y": 15_788_030,     # 17.266 inches
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_D_PILL = {
    "x": 1_039_499,
    "y": 17_724_729,     # 19.384 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_D_TEXT = {
    "x": 3_107_605,
    "y": 17_924_068,     # 19.602 inches
    "width": 32_744_401,
    "height": 1_597_340,
}

MCQ_OPTIONS = [
    {"label": "A", "pill": OPTION_A_PILL, "label_box": OPTION_A_LABEL, "text_box": OPTION_A_TEXT},
    {"label": "B", "pill": OPTION_B_PILL, "label_box": None, "text_box": OPTION_B_TEXT},
    {"label": "C", "pill": OPTION_C_PILL, "label_box": None, "text_box": OPTION_C_TEXT},
    {"label": "D", "pill": OPTION_D_PILL, "label_box": None, "text_box": OPTION_D_TEXT},
]

# ============================================================================
# SECTION 5: MCQ OPTIONS, 2-COLUMN GRID (defence template only)
#
# The defence template's title banner already reserves space at the top, so
# on that template the single vertical column above runs off the bottom of
# the slide (see defence_grid_layout.svg in this folder). Only there, options
# regroup into two columns: A/B on row 0, C/D on row 1. Left-column x/width
# are unchanged from above; the right column mirrors qpill_qtext_image_mcq's
# HALF_SLIDE_EMU / COLUMN_GAP_EMU split for its second column.
# ============================================================================

_INCH_EMU = 914_400
_SLIDE_WIDTH_EMU = 40 * _INCH_EMU
_HALF_SLIDE_EMU = _SLIDE_WIDTH_EMU // 2
_GRID_COLUMN_GAP_EMU = int(0.2 * _INCH_EMU)

_GRID_PILL_TO_TEXT_DX = OPTION_A_TEXT["x"] - OPTION_A_PILL["x"]
_GRID_RIGHT_PILL_X = _HALF_SLIDE_EMU + _GRID_COLUMN_GAP_EMU
_GRID_RIGHT_TEXT_X = _GRID_RIGHT_PILL_X + _GRID_PILL_TO_TEXT_DX

_GRID_LEFT_TEXT_WIDTH = _HALF_SLIDE_EMU - OPTION_A_TEXT["x"] - _GRID_COLUMN_GAP_EMU
_GRID_RIGHT_TEXT_WIDTH = _SLIDE_WIDTH_EMU - _GRID_RIGHT_TEXT_X - QUESTION_TEXT["x"]

_GRID_ROW_GAP = OPTION_B_PILL["y"] - OPTION_A_PILL["y"]
_GRID_TEXT_ROW_GAP = OPTION_B_TEXT["y"] - OPTION_A_TEXT["y"]

_GRID_LABEL_DX = OPTION_A_LABEL["x"] - OPTION_A_PILL["x"]
_GRID_LABEL_DY = OPTION_A_LABEL["y"] - OPTION_A_PILL["y"]

_GRID_COLUMN_X = {
    "pill": [OPTION_A_PILL["x"], _GRID_RIGHT_PILL_X],
    "text": [OPTION_A_TEXT["x"], _GRID_RIGHT_TEXT_X],
    "text_width": [_GRID_LEFT_TEXT_WIDTH, _GRID_RIGHT_TEXT_WIDTH],
}


def _grid_options(dspec=None) -> list[dict]:
    """MCQ option rows A-D arranged in a 2-column grid (defence-aware y shift)."""
    options = []
    for i, letter in enumerate(("A", "B", "C", "D")):
        col = i % 2
        row = i // 2
        pill_x = _GRID_COLUMN_X["pill"][col]
        pill_y = _shift_y(OPTION_A_PILL["y"] + row * _GRID_ROW_GAP, dspec)
        pill = {"x": pill_x, "y": pill_y, "width": OPTION_A_PILL["width"], "height": OPTION_A_PILL["height"]}
        text_box = {
            "x": _GRID_COLUMN_X["text"][col],
            "y": _shift_y(OPTION_A_TEXT["y"] + row * _GRID_TEXT_ROW_GAP, dspec),
            "width": _GRID_COLUMN_X["text_width"][col],
            "height": OPTION_A_TEXT["height"],
        }
        label_box = {
            "x": pill_x + _GRID_LABEL_DX,
            "y": pill_y + _GRID_LABEL_DY,
            "width": OPTION_A_LABEL["width"],
            "height": OPTION_A_LABEL["height"],
        }
        options.append({"label": letter, "pill": pill, "label_box": label_box, "text_box": text_box})
    return options


def _shift_y(y: int, dspec=None) -> int:
    if dspec is not None and dspec.has_top_banner():
        return dspec.y_below_banner(y)
    return y


def _box_for(box: dict[str, int], dspec=None) -> dict[str, int]:
    return {**box, "y": _shift_y(box["y"], dspec)}


def question_text_for(dspec=None) -> dict[str, int]:
    pill_y = _shift_y(QUESTION_PILL["y"], dspec)
    y = pill_y + QUESTION_PILL["height"] + PILL_TO_TEXT_GAP_EMU
    return {
        "x": QUESTION_TEXT["x"],
        "y": y,
        "width": QUESTION_TEXT["width"],
        "height": QUESTION_TEXT["height"],
    }


def table_box_for(dspec=None) -> dict[str, int]:
    return {
        "x": TABLE_BOX["x"],
        "y": _shift_y(TABLE_BOX["y"], dspec),
        "width": TABLE_BOX["width"],
        "height": TABLE_BOX["height"],
    }


def _option_row_for(row: dict, dspec=None) -> dict:
    return {
        "label": row["label"],
        "pill": _box_for(row["pill"], dspec),
        "label_box": _box_for(row["label_box"], dspec) if row["label_box"] is not None else None,
        "text_box": _box_for(row["text_box"], dspec),
    }


def mcq_options_for(dspec=None) -> list[dict]:
    """MCQ option rows A-D below the table.

    Defence template (dspec.has_top_banner()): 2-column grid, since the title
    banner already reserves top space and the single-column layout would run
    past the bottom of the slide. Every other template: unchanged single
    column.
    """
    if dspec is not None and dspec.has_top_banner():
        return _grid_options(dspec)
    return [_option_row_for(row, dspec) for row in MCQ_OPTIONS]
