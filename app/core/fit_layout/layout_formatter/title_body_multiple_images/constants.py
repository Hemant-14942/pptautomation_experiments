"""Fixed textbox coordinates for the title_body_multiple_images slide type.

Same as title_body_single_image for body content (left side).
For images (right side): use full available width (body box end to slide edge),
with special handling for 2 images (45% height each with small gap).

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches). 1 inch = 914,400 EMU.
"""

# Body content textbox (left side, unchanged from single_image).
# Position: 1.0in from left, 5.151in from top.
# Size: 23.406in x 19.015in.
BODY_TEXTBOX = {
    "x": 914400,
    "y": 4711025,
    "width": 21409273,
    "height": 17393675,
}

# Slide canvas dimensions
SLIDE_WIDTH_EMU = 36_576_000  # 40 inches
SLIDE_HEIGHT_EMU = 20_574_000  # 22.5 inches

# Right-side image area: starts where body begins, extends to slide right edge and bottom.
# Body begins at: y = 4711025 EMU (5.151in)
# Image area must end at or before slide bottom: 20,574,000 EMU (22.5in)
# Available height for images: 20574000 - 4711025 = 15,862,975 EMU (~17.36in)
# Body ends at: x + width = 914400 + 21409273 = 22323673 EMU = 24.406in
IMAGE_AREA = {
    "x": BODY_TEXTBOX["x"] + BODY_TEXTBOX["width"],
    "y": BODY_TEXTBOX["y"],
    "width": SLIDE_WIDTH_EMU - (BODY_TEXTBOX["x"] + BODY_TEXTBOX["width"]),
    "height": SLIDE_HEIGHT_EMU - BODY_TEXTBOX["y"],  # from body start to slide bottom
}


def get_image_boxes(num_images: int) -> list[dict[str, int]]:
    """Divide IMAGE_AREA into num_images boxes stacked vertically.

    Special case for 2 images: each 45% height with small vertical gap (~5%).
    For 3+ images: divide height equally (height / num_images per image).
    """
    if num_images < 1:
        return []

    if num_images == 2:
        # Two images: 45% height each, small 5% gap between them
        height_per_image = round(IMAGE_AREA["height"] * 0.45)
        gap = round(IMAGE_AREA["height"] * 0.05)
        return [
            {
                "x": IMAGE_AREA["x"],
                "y": IMAGE_AREA["y"],
                "width": IMAGE_AREA["width"],
                "height": height_per_image,
            },
            {
                "x": IMAGE_AREA["x"],
                "y": IMAGE_AREA["y"] + height_per_image + gap,
                "width": IMAGE_AREA["width"],
                "height": height_per_image,
            },
        ]
    else:
        # 3+ images: equal height division
        height_per_image = IMAGE_AREA["height"] // num_images
        boxes = []
        for i in range(num_images):
            boxes.append(
                {
                    "x": IMAGE_AREA["x"],
                    "y": IMAGE_AREA["y"] + (i * height_per_image),
                    "width": IMAGE_AREA["width"],
                    "height": height_per_image,
                }
            )
        return boxes
