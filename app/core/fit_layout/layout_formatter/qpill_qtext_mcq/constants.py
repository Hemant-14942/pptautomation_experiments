"""Position and size rules for question + text + MCQ slides.

Extracted from p.pptx slide 24. All values remain constant across all
question-with-MCQ slides. This layout includes:
1. Question pill shape with label
2. Question text box (multi-line)
3. Four MCQ options (A, B, C, D) each with pill + answer text

Canvas dimensions: 36,576,000 × 20,574,000 EMU (40 × 22.5 inches).
Conversion: 1 inch = 914,400 EMU.
"""

# ============================================================================
# SECTION 1: QUESTION PILL (Top)
# ============================================================================

# The question pill is a rounded rectangle that appears at the top
# Position: x=-2.039" (extends left), y=0.746" from top
# Size: 7.745" × 1.717"
QUESTION_PILL = {
    "x": -1_864_528,     # Left edge: -2.039 inches
    "y": 681_774,        # Top edge: 0.746 inches
    "width": 7_081_988,  # Width: 7.745 inches
    "height": 1_569_660, # Height: 1.717 inches
}

# The question label text sits INSIDE the question pill
# Contains text like "Question"
# Position: x=1.137", y=0.904"
# Size: 4.989" × 1.111"
QUESTION_LABEL = {
    "x": 1_039_500,      # Left edge: 1.137 inches
    "y": 827_049,        # Top edge: 0.904 inches
    "width": 4_562_190,  # Width: 4.989 inches
    "height": 1_015_622, # Height: 1.111 inches
}

# ============================================================================
# SECTION 2: QUESTION TEXT BOX (Below pill with gap)
# ============================================================================

# The question text box appears below the pill and contains the actual question
# This can be multi-line (4-5 lines of text) with wrapping enabled
# Position: x=1.208", y=2.621" (starts below pill with ~1.2" gap)
# Size: 38.0" × 2.8" (full width-ish)
QUESTION_TEXT = {
    "x": 1_104_806,      # Left edge: 1.208 inches
    "y": 2_396_709,      # Top edge: 2.621 inches (below pill)
    "width": 34_747_200, # Width: 38.0 inches (full width)
    "height": 2_560_560, # Height: 2.8 inches (room for multi-line text)
}

# ============================================================================
# SECTION 3: MCQ OPTIONS (Below question text with gap)
# ============================================================================

# MCQ Options A, B, C, D each have:
# 1. A pill shape (ellipse) with label inside
# 2. Answer text box to the right of the pill

# OPTION A
# Position: y=12.438" (below question text with ~7" gap)
OPTION_A_PILL = {
    "x": 1_039_500,      # Left edge: 1.137 inches
    "y": 11_381_672,     # Top edge: 12.438 inches
    "width": 1_596_024,  # Width: 1.747 inches (ellipse)
    "height": 1_596_024, # Height: 1.747 inches (ellipse)
}

OPTION_A_LABEL = {
    "x": 1_104_806,      # Left edge: 1.208 inches (slightly right of pill center)
    "y": 11_565_696,     # Top edge: 12.655 inches
    "width": 1_465_704,  # Width: 1.604 inches
    "height": 1_169_352, # Height: 1.279 inches
}

OPTION_A_TEXT = {
    "x": 3_105_144,      # Left edge: 3.399 inches (right of pill with gap)
    "y": 13_709_904,     # Top edge: 15.006 inches
    "width": 32_758_992, # Width: 35.810 inches (rest of slide)
    "height": 1_596_024, # Height: 1.747 inches
}

# OPTION B (gap ~0.3" from Option A)
# Position: y=14.753"
OPTION_B_PILL = {
    "x": 1_039_500,      # Left edge: 1.137 inches
    "y": 13_481_952,     # Top edge: 14.753 inches
    "width": 1_596_024,  # Width: 1.747 inches
    "height": 1_596_024, # Height: 1.747 inches
}

OPTION_B_LABEL = {
    "x": 1_104_806,
    "y": 13_665_976,
    "width": 1_465_704,
    "height": 1_169_352,
}

OPTION_B_TEXT = {
    "x": 3_105_144,      # Left edge: 3.399 inches
    "y": 13_709_904,     # Top edge: 15.006 inches (same row as option A text - WAIT, check slide 24)
    "width": 32_758_992, # Width: 35.810 inches
    "height": 1_596_024, # Height: 1.747 inches
}

# OPTION C (gap ~0.3" from Option B)
# Position: y=17.069"
OPTION_C_PILL = {
    "x": 1_039_500,      # Left edge: 1.137 inches
    "y": 15_599_296,     # Top edge: 17.069 inches
    "width": 1_596_024,  # Width: 1.747 inches
    "height": 1_596_024, # Height: 1.747 inches
}

OPTION_C_LABEL = {
    "x": 1_104_806,
    "y": 15_783_320,
    "width": 1_465_704,
    "height": 1_169_352,
}

OPTION_C_TEXT = {
    "x": 3_105_144,      # Left edge: 3.399 inches
    "y": 15_781_224,     # Top edge: 17.266 inches
    "width": 32_758_992, # Width: 35.810 inches
    "height": 1_596_024, # Height: 1.747 inches
}

# OPTION D (gap ~0.3" from Option C)
# Position: y=19.384"
OPTION_D_PILL = {
    "x": 1_039_500,      # Left edge: 1.137 inches
    "y": 17_716_640,     # Top edge: 19.384 inches
    "width": 1_596_024,  # Width: 1.747 inches
    "height": 1_596_024, # Height: 1.747 inches
}

OPTION_D_LABEL = {
    "x": 1_104_806,
    "y": 17_900_664,
    "width": 1_465_704,
    "height": 1_169_352,
}

OPTION_D_TEXT = {
    "x": 3_105_144,      # Left edge: 3.399 inches
    "y": 17_898_568,     # Top edge: 19.602 inches
    "width": 32_758_992, # Width: 35.810 inches
    "height": 1_596_024, # Height: 1.747 inches
}

# ============================================================================
# MCQ OPTIONS LIST (for iteration)
# ============================================================================

MCQ_OPTIONS = [
    {
        "label": "A",
        "pill": OPTION_A_PILL,
        "label_box": OPTION_A_LABEL,
        "text_box": OPTION_A_TEXT,
    },
    {
        "label": "B",
        "pill": OPTION_B_PILL,
        "label_box": OPTION_B_LABEL,
        "text_box": OPTION_B_TEXT,
    },
    {
        "label": "C",
        "pill": OPTION_C_PILL,
        "label_box": OPTION_C_LABEL,
        "text_box": OPTION_C_TEXT,
    },
    {
        "label": "D",
        "pill": OPTION_D_PILL,
        "label_box": OPTION_D_LABEL,
        "text_box": OPTION_D_TEXT,
    },
]
