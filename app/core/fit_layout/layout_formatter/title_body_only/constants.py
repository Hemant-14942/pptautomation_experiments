"""Fixed textbox coordinates for the title_body_only slide type.

Body textbox is full-width-ish (80% of slide), centered vertically with
the content inside it.

Canvas: 36,576,000 × 20,574,000 EMU (40 × 22.5 inches). 1 inch = 914,400 EMU.
"""

# Body content textbox (full width minus right margin, no image area needed).
# Position: 1.0" from left, 5.151" from top (below heading pill).
# Size: 32" wide (80% of 40" slide width) × 19.015" tall (to slide bottom).
# Text is left-aligned horizontally and centered vertically within the box.
BODY_TEXTBOX = {
    "x": 914400,
    "y": 4711025,
    "width": 29260560,
    "height": 17393675,
}
