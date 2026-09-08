"""Position and size rules for question + text + MCQ slides.

Extracted from p.pptx slide 29 (index 28). All values remain constant
across all question-with-MCQ slides. This layout includes:
1. Question pill shape with label
2. Question text box (multi-line)
3. Four MCQ options (A, B, C, D) each with pill + answer text

Canvas dimensions: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches).
Conversion: 1 inch = 914,400 EMU.

Option A's pill and its "A" label are separate top-level shapes in the
source deck. Options B, C, D each have their pill and label already
grouped (<p:grpSp>) by the designer, so repositioning them only needs a
rigid-body translation of the group (see xml_utils.place_group) -- no
separate label constants are needed for B/C/D.
"""

# ============================================================================
# SECTION 1: QUESTION PILL (Top, bleeds off the left edge)
# ============================================================================

QUESTION_PILL = {
    "x": -1_864_528,     # Left edge: -2.039 inches
    "y": 681_774,        # Top edge: 0.746 inches
    "width": 7_081_988,  # Width: 7.745 inches
    "height": 1_569_660, # Height: 1.717 inches
}

# The question label text sits INSIDE the question pill (text: "Question")
QUESTION_LABEL = {
    "x": 1_039_500,      # Left edge: 1.137 inches
    "y": 827_049,        # Top edge: 0.904 inches
    "width": 4_562_190,  # Width: 4.989 inches
    "height": 1_015_622, # Height: 1.111 inches
}

# ============================================================================
# SECTION 2: QUESTION TEXT BOX (Below pill with gap)
# ============================================================================

# Height set to 4.8in (matches the real slide's gap to option A) so
# multi-line questions have room; auto-fit should shrink the font if the
# question text still overflows this fixed box.
QUESTION_TEXT = {
    "x": 1_104_806,      # Left edge: 1.208 inches
    "y": 2_396_709,      # Top edge: 2.621 inches (below pill)
    "width": 34_747_200, # Width: 38.0 inches
    "height": 4_389_120, # Height: 4.8 inches
}

# ============================================================================
# SECTION 3: MCQ OPTIONS (Below question text, ~0.57in gap between rows)
# ============================================================================

OPTION_A_PILL = {
    "x": 1_039_499,
    "y": 8_105_829,      # 8.865 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_A_LABEL = {
    "x": 1_104_807,
    "y": 8_304_334,
    "width": 1_466_700,
    "height": 1_169_511,
}

OPTION_A_TEXT = {
    "x": 3_107_605,
    "y": 8_396_618,
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_B_PILL = {
    "x": 1_039_499,
    "y": 10_223_169,     # 11.180 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_B_TEXT = {
    "x": 3_107_605,
    "y": 10_453_760,
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_C_PILL = {
    "x": 1_039_499,
    "y": 12_340_509,     # 13.496 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_C_TEXT = {
    "x": 3_107_605,
    "y": 12_521_075,
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_D_PILL = {
    "x": 1_039_499,
    "y": 14_457_849,     # 15.811 inches
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_D_TEXT = {
    "x": 3_107_605,
    "y": 14_656_354,
    "width": 32_744_401,
    "height": 1_597_340,
}

# ============================================================================
# MCQ OPTIONS LIST (for iteration)
# ============================================================================

MCQ_OPTIONS = [
    {"label": "A", "pill": OPTION_A_PILL, "label_box": OPTION_A_LABEL, "text_box": OPTION_A_TEXT},
    {"label": "B", "pill": OPTION_B_PILL, "label_box": None, "text_box": OPTION_B_TEXT},
    {"label": "C", "pill": OPTION_C_PILL, "label_box": None, "text_box": OPTION_C_TEXT},
    {"label": "D", "pill": OPTION_D_PILL, "label_box": None, "text_box": OPTION_D_TEXT},
]
