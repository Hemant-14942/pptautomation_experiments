"""Fit an image into a fixed target box, preserving aspect ratio.

No pixel-level resizing happens here. A PPTX picture's on-slide size is
just its <a:ext> EMU width/height — PowerPoint scales the embedded image
to whatever frame we give it. So "resizing" means computing the EMU
width/height (and a centering offset) that fits the image's pixel aspect
ratio inside the target box, via python-pptx's `picture.image.size`.
"""


def fit_image_to_box(
    image_width_px: int, image_height_px: int, box: dict[str, int]
) -> dict[str, int]:
    """Return {x, y, width, height} (EMU) fitting the image inside box.

    Contain-fit: the image is scaled down to fit entirely within the box
    while preserving its aspect ratio, then centered in the box on
    whichever axis has leftover space.
    """
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
