"""Fixed textbox coordinates for the title_body_single_image slide type.

Values extracted from slide 6 of app/data/output/test3.pptx and slide 1 of
app/data/output/test2.pptx (heading pill bottom edge matched at ~4.605in in
both, confirming the canvas layout is consistent across templates).

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches). 1 inch = 914,400 EMU.
"""

SLIDE_HEIGHT_EMU = 20_574_000  # 22.5 inches

# Empty space at the bottom of the slide (same convention as table_only).
BOTTOM_MARGIN_EMU = 914_400  # 1 inch

# Body content textbox (left side, wrap mode on, left-aligned).
# Position: 1.0in from left, 5.151in from top (starts below the heading pill).
# Height: down to a 1in bottom margin (was hardcoded past the slide edge
# before — height must track slide_height - y - bottom_margin, not a fixed
# 19.015in that outlives the actual available space).
BODY_TEXTBOX = {
    "x": 914400,
    "y": 4711025,
    "width": 21409273,
    "height": SLIDE_HEIGHT_EMU - 4711025 - BOTTOM_MARGIN_EMU,  # 16.349in tall
}

# Image textbox (right side). Image is resized to fit inside this box only
# when it doesn't already fit — aspect ratio is preserved.
# Position: 25.196in from left, 7.417in from top.
# Size: 12.98in x 8.174in.
IMAGE_TEXTBOX = {
    "x": 23055193,
    "y": 6783665,
    "width": 11880273,
    "height": 7478618,
}
