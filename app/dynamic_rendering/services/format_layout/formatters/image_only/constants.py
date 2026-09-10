"""Fixed image box layout for image_only slides.

An image_only slide has NO heading, NO body text, NO table — only pictures.

Canvas: 40 inches wide x 22.5 inches tall.
1 inch = 914,400 EMU.
"""

import math

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 40 * INCH_EMU
SLIDE_HEIGHT_EMU = 22.5 * INCH_EMU

# Empty space around the whole slide.
SIDE_MARGIN_EMU = 2 * INCH_EMU  # 2 inch on each side

# Small gap between images so they do not touch.
IMAGE_GAP_EMU = INCH_EMU // 2  # 0.5 inch

# ---------------------------------------------------------------------------
# TUNING KNOBS — change these numbers to make images bigger or smaller
# ---------------------------------------------------------------------------
# All values are fractions (0.0 to 1.0). Lower = smaller image, more empty space.

# 1 image: how much of the content area the slot box uses (was 0.85, too big).
SINGLE_IMAGE_FILL = 0.60  # try 0.55 (smaller) or 0.70 (bigger)

# 2+ images: how much of each grid cell the slot box uses.
# 2-image slides looked too tall because cell_h was 100% of slide height.
MULTI_IMAGE_CELL_FILL_W = 0.90  # width of each cell (0.9 = 90%)
MULTI_IMAGE_CELL_FILL_H = 0.70  # height of each cell (0.7 = 70% — lowers tall images)

# The area where all images live (inside the margins).
CONTENT_AREA = {
    "x": SIDE_MARGIN_EMU,
    "y": SIDE_MARGIN_EMU,
    "width": SLIDE_WIDTH_EMU - 2 * SIDE_MARGIN_EMU,
    "height": SLIDE_HEIGHT_EMU - 2 * SIDE_MARGIN_EMU,
}


def _shrink_and_center(box: dict[str, int], fill_w: float, fill_h: float) -> dict[str, int]:
    """Make a slot box smaller and keep it centered in its region.

    Example: fill_w=0.9, fill_h=0.7 means the slot uses 90% of width
    and 70% of height, with equal empty space on all sides.
    """
    w = int(box["width"] * fill_w)
    h = int(box["height"] * fill_h)
    return {
        "x": box["x"] + (box["width"] - w) // 2,
        "y": box["y"] + (box["height"] - h) // 2,
        "width": w,
        "height": h,
    }


def get_image_boxes(
    num_images: int,
    layout: str = "balanced",
    content_area: dict[str, int] | None = None,
) -> list[dict[str, int]]:
    """Return a list of slot boxes for each image on the slide.

    Each box is a dict with x, y, width, height in EMU.
    The formatter will place each picture inside its slot (aspect ratio kept).

    Layout rules:
      1 image  -> one big box in the center (85% of slide area)
      2 images -> left half | right half
      3 images -> 2 on top row, 1 on bottom (see layout flag)
      4 images -> 2x2 grid
      5+ images -> auto grid (cols = ceil(sqrt(n)))

    layout:
      "balanced"  -> 3rd image centered on bottom row (recommended, looks even)
      "bottom_left" -> 3rd image under the left image (your original idea)
    """
    if num_images < 1:
        return []

    area = content_area if content_area is not None else CONTENT_AREA
    gap = IMAGE_GAP_EMU

    # --- 1 image: centered hero box (size controlled by SINGLE_IMAGE_FILL) ---
    if num_images == 1:
        box_w = int(area["width"] * SINGLE_IMAGE_FILL)
        box_h = int(area["height"] * SINGLE_IMAGE_FILL)
        return [{
            "x": area["x"] + (area["width"] - box_w) // 2,
            "y": area["y"] + (area["height"] - box_h) // 2,
            "width": box_w,
            "height": box_h,
        }]

    # --- 2 images: side by side (each cell shrunk by MULTI_IMAGE_CELL_FILL_*) ---
    if num_images == 2:
        cell_w = (area["width"] - gap) // 2
        cell_h = area["height"]
        raw = [
            {"x": area["x"], "y": area["y"], "width": cell_w, "height": cell_h},
            {
                "x": area["x"] + cell_w + gap,
                "y": area["y"],
                "width": cell_w,
                "height": cell_h,
            },
        ]
        return [
            _shrink_and_center(b, MULTI_IMAGE_CELL_FILL_W, MULTI_IMAGE_CELL_FILL_H)
            for b in raw
        ]

    # --- 3 images: two on top, one on bottom ---
    if num_images == 3:
        row_h = (area["height"] - gap) // 2
        cell_w = (area["width"] - gap) // 2

        top_left = {"x": area["x"], "y": area["y"], "width": cell_w, "height": row_h}
        top_right = {
            "x": area["x"] + cell_w + gap,
            "y": area["y"],
            "width": cell_w,
            "height": row_h,
        }

        if layout == "bottom_left":
            # Third image sits under image 1 (left column).
            bottom = {
                "x": area["x"],
                "y": area["y"] + row_h + gap,
                "width": cell_w,
                "height": row_h,
            }
        else:
            # Third image centered on bottom row (more balanced look).
            bottom = {
                "x": area["x"] + (area["width"] - cell_w) // 2,
                "y": area["y"] + row_h + gap,
                "width": cell_w,
                "height": row_h,
            }

        raw = [top_left, top_right, bottom]
        return [
            _shrink_and_center(b, MULTI_IMAGE_CELL_FILL_W, MULTI_IMAGE_CELL_FILL_H)
            for b in raw
        ]

    # --- 4 images: 2x2 grid ---
    if num_images == 4:
        cell_w = (area["width"] - gap) // 2
        cell_h = (area["height"] - gap) // 2
        raw = [
            {"x": area["x"], "y": area["y"], "width": cell_w, "height": cell_h},
            {"x": area["x"] + cell_w + gap, "y": area["y"], "width": cell_w, "height": cell_h},
            {"x": area["x"], "y": area["y"] + cell_h + gap, "width": cell_w, "height": cell_h},
            {
                "x": area["x"] + cell_w + gap,
                "y": area["y"] + cell_h + gap,
                "width": cell_w,
                "height": cell_h,
            },
        ]
        return [
            _shrink_and_center(b, MULTI_IMAGE_CELL_FILL_W, MULTI_IMAGE_CELL_FILL_H)
            for b in raw
        ]

    # --- 5+ images: auto grid ---
    cols = math.ceil(math.sqrt(num_images))
    rows = math.ceil(num_images / cols)
    cell_w = (area["width"] - gap * (cols - 1)) // cols
    cell_h = (area["height"] - gap * (rows - 1)) // rows

    boxes = []
    for i in range(num_images):
        row = i // cols
        col = i % cols
        raw = {
            "x": area["x"] + col * (cell_w + gap),
            "y": area["y"] + row * (cell_h + gap),
            "width": cell_w,
            "height": cell_h,
        }
        boxes.append(
            _shrink_and_center(raw, MULTI_IMAGE_CELL_FILL_W, MULTI_IMAGE_CELL_FILL_H)
        )
    return boxes
