
# The pill shape is a rounded rectangle that holds the question label.
# It extends beyond the slide's left edge (negative X value is intentional).
# Position x=-2.039" means it starts 2.039 inches to the LEFT of the slide edge.
# Position y=0.746" means it starts 0.746 inches from the top of the slide.
# Width 7.745" and height 1.717" are the pill's dimensions in inches.
QUESTION_PILL = {
    "x": -1_864_528,     # Left edge position: -2.039 inches (extends left of slide)
    "y": 681_774,        # Top edge position: 0.746 inches from slide top
    "width": 7_081_988,  # Pill width: 7.745 inches
    "height": 1_569_660, # Pill height: 1.717 inches
}

# The label text box sits INSIDE the pill shape.
# This is where text like "Question" or "Option A" appears.
# Position x=1.137" and y=0.904" are measured from the slide's left-top corner.
# Width 4.989" and height 1.111" are the text box dimensions.
QUESTION_LABEL = {
    "x": 1_039_500,      # Text box left edge: 1.137 inches from slide left
    "y": 827_049,        # Text box top edge: 0.904 inches from slide top
    "width": 4_562_190,  # Text box width: 4.989 inches
    "height": 1_015_622, # Text box height: 1.111 inches
}

# The question body text box appears BELOW the pill shape.
# This is where the actual question content appears (e.g., "Find the cofactors of A").
# Position x=1.208" and y=2.621" are measured from the slide's left-top corner.
# Width 38.0" and height 3.8" give plenty of room for multi-line question text.
# Text wrapping is enabled for this box so long questions wrap vertically.
QUESTION_BODY = {
    "x": 1_104_806,       # Text box left edge: 1.208 inches from slide left
    "y": 2_396_709,       # Text box top edge: 2.621 inches from slide top (below pill)
    "width": 34_747_200,  # Text box width: 38.0 inches (full-width-ish)
    "height": 3_474_720,  # Text box height: 3.8 inches (plenty of room for text)
}
