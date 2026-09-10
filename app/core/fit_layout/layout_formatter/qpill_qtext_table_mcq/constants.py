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

# Text fit order (question + answer boxes):
#   1. wrap="square"  — long lines break to next row (no spill off right edge)
#   2. normAutofit      — if wrapped text still too tall, shrink font to fit
QUESTION_TEXT = {
    "x": 1_104_806,      # 1.208 inches
    "y": 2_396_709,      # 2.621 inches
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
