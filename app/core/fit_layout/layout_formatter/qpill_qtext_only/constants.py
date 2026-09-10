"""Fixed layout for question pill + question text only (no table, no MCQ).

Extracted from app/data/input/p.pptx slide 17 (index 16).

Layout:
  1. Question pill + "Question" label (same position as all qpill types)
  2. Question text box below pill — top-left aligned, wrap + normAutofit

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches).
1 inch = 914,400 EMU.

Margins on reference slide 17:
  left:  1.208 inches (question text left edge)
  right: 0.792 inches (40 - 1.208 - 38.0)
  gap pill bottom to text top: ~0.16 inches

Question text height: 60% of slide height (13.5 inches).
"""

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 40 * INCH_EMU       # 36,576,000
SLIDE_HEIGHT_EMU = 22.5 * INCH_EMU    # 20,574,000

# Left edge of question text — matches slide 17 and other qpill types
CONTENT_LEFT_EMU = 1_104_806          # 1.208 inches
CONTENT_WIDTH_EMU = 34_747_200        # 38.0 inches (full width minus side gaps)

# Gap between question pill bottom and question text top (slide 17)
PILL_TO_TEXT_GAP_EMU = 145_275        # ~0.159 inches

# ============================================================================
# SECTION 1: QUESTION PILL (top, bleeds off left edge — same as all qpill types)
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
# SECTION 2: QUESTION TEXT BOX (below pill, 60% slide height)
# ============================================================================

# Text fit: wrap="square" first, then normAutofit shrinks font if still too tall.
# Alignment: top-left (anchor="t", algn="l") — text starts at top of box.
QUESTION_TEXT = {
    "x": CONTENT_LEFT_EMU,
    "y": QUESTION_PILL["y"] + QUESTION_PILL["height"] + PILL_TO_TEXT_GAP_EMU,
    "width": CONTENT_WIDTH_EMU,
    "height": int(0.6 * SLIDE_HEIGHT_EMU),  # 13.5 inches = 12,344,400 EMU
}
