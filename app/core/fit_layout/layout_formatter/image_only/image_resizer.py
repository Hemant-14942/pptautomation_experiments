"""Scale each picture to fit inside its slot box without stretching.

Same logic as title_body_single_image and title_body_multiple_images:
  - keep the image aspect ratio (no squashing)
  - center the image inside the orange slot box from constants.py
"""


def fit_image_to_box(
    image_width_px: int, image_height_px: int, box: dict[str, int]
) -> dict[str, int]:
    """Return the final x, y, width, height for one picture in EMU.

    Args:
        image_width_px:  original image width in pixels
        image_height_px: original image height in pixels
        box:             slot dict from get_image_boxes() with x, y, width, height

    Returns:
        dict with x, y, width, height — picture fits inside box, centered.
    """
    # Compare image shape vs box shape (wide vs tall)
    image_aspect = image_width_px / image_height_px
    box_aspect = box["width"] / box["height"]

    if image_aspect > box_aspect:
        # Image is wider than the box — limit by width, shrink height to match
        width = box["width"]
        height = round(width / image_aspect)
    else:
        # Image is taller than the box — limit by height, shrink width to match
        height = box["height"]
        width = round(height * image_aspect)

    # Center the fitted image inside the slot box
    x = box["x"] + (box["width"] - width) // 2
    y = box["y"] + (box["height"] - height) // 2

    return {"x": x, "y": y, "width": width, "height": height}
