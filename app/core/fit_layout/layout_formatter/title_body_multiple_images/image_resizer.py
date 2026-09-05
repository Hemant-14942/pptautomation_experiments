"""Fit multiple images into their assigned boxes, preserving aspect ratio.

Reuses the same contain-fit logic as title_body_single_image: scale each
image down (or up, if tiny) to fit entirely within its box while preserving
aspect ratio, then center it in the box.
"""


def fit_image_to_box(
    image_width_px: int, image_height_px: int, box: dict[str, int]
) -> dict[str, int]:
   
    image_aspect = image_width_px / image_height_px
    box_aspect = box["width"] / box["height"]

    if image_aspect > box_aspect:
        # Image is relatively wider than the box -> width-constrained.
        width = box["width"]
        height = round(width / image_aspect)
    else:
        # Image is relatively taller than (or equal to) the box -> height-constrained.
        height = box["height"]
        width = round(height * image_aspect)

    x = box["x"] + (box["width"] - width) // 2
    y = box["y"] + (box["height"] - height) // 2

    return {"x": x, "y": y, "width": width, "height": height}
