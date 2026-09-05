"""Fixed textbox coordinates for the title_body_single_image slide type.

Values extracted from slide 6 of app/data/output/test3.pptx and slide 1 of
app/data/output/test2.pptx (heading pill bottom edge matched at ~4.605in in
both, confirming the canvas layout is consistent across templates).

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches). 1 inch = 914,400 EMU.
"""

# Body content textbox (left side, wrap mode on, left-aligned).
# Position: 1.0in from left, 5.151in from top (starts below the heading pill).
# Size: 23.406in x 19.015in.
BODY_TEXTBOX = {
    "x": 914400,
    "y": 4711025,
    "width": 21409273,
    "height": 17393675,
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
