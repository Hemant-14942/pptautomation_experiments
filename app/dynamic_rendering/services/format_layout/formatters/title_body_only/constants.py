"""Fixed textbox coordinates for the title_body_only slide type.

Body textbox is full-width-ish (80% of slide), centered vertically with
the content inside it.

Canvas: 36,576,000 × 20,574,000 EMU (40 × 22.5 inches). 1 inch = 914,400 EMU.
"""

SLIDE_HEIGHT_EMU = 20_574_000  # 22.5 inches

# Empty space at the bottom of the slide (same convention as table_only).
BOTTOM_MARGIN_EMU = 914_400  # 1 inch

# Body content textbox (full width minus right margin, no image area needed).
# Position: 1.0" from left, 5.151" from top (below heading pill).
# Height: down to a 1" bottom margin (was hardcoded past the slide edge
# before — height must track slide_height - y - bottom_margin, not a fixed
# 19.015" that outlives the actual available space).
# Text is left-aligned horizontally and centered vertically within the box.
BODY_TEXTBOX = {
    "x": 914400,
    "y": 4711025,
    "width": 29260560,
    "height": SLIDE_HEIGHT_EMU - 4711025 - BOTTOM_MARGIN_EMU,  # 16.349" tall
}
