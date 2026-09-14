"""Fixed textbox coordinates for the title_body_multiple_images slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    SLIDE_WIDTH_EMU,
    content_height_for,
    content_start_y_for,
)

BODY_TEXTBOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": 21_409_273,
    "height": content_height_for(CONTENT_START_Y),
}

IMAGE_AREA = {
    "x": BODY_TEXTBOX["x"] + BODY_TEXTBOX["width"],
    "y": BODY_TEXTBOX["y"],
    "width": SLIDE_WIDTH_EMU - (BODY_TEXTBOX["x"] + BODY_TEXTBOX["width"]),
    "height": content_height_for(BODY_TEXTBOX["y"]),
}


def get_image_boxes(num_images: int) -> list[dict[str, int]]:
    if num_images < 1:
        return []

    if num_images == 2:
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

    height_per_image = IMAGE_AREA["height"] // num_images
    return [
        {
            "x": IMAGE_AREA["x"],
            "y": IMAGE_AREA["y"] + (i * height_per_image),
            "width": IMAGE_AREA["width"],
            "height": height_per_image,
        }
        for i in range(num_images)
    ]


def body_textbox_for(dspec=None) -> dict:
    """Body textbox below the title pill; bottom edge respects BOTTOM_MARGIN_EMU."""
    y = content_start_y_for(dspec)
    return {
        "x": CONTENT_LEFT_X,
        "y": y,
        "width": 21_409_273,
        "height": content_height_for(y),
    }


def image_area_for(dspec=None) -> dict:
    """Right-side image column aligned with body top and bottom margin."""
    body = body_textbox_for(dspec)
    return {
        "x": body["x"] + body["width"],
        "y": body["y"],
        "width": SLIDE_WIDTH_EMU - (body["x"] + body["width"]),
        "height": content_height_for(body["y"]),
    }


def image_boxes_for(num_images: int, dspec=None) -> list[dict[str, int]]:
    """Per-image boxes inside the (defence-aware) image area.

    Defence variant just calls this with dspec; standard callers pass dspec=None
    and get the same boxes as the legacy get_image_boxes() helper.
    """
    if num_images < 1:
        return []

    area = image_area_for(dspec)
    if num_images == 2:
        height_per_image = round(area["height"] * 0.45)
        gap = round(area["height"] * 0.05)
        return [
            {"x": area["x"], "y": area["y"],
             "width": area["width"], "height": height_per_image},
            {"x": area["x"], "y": area["y"] + height_per_image + gap,
             "width": area["width"], "height": height_per_image},
        ]

    height_per_image = area["height"] // num_images
    return [
        {"x": area["x"], "y": area["y"] + (i * height_per_image),
         "width": area["width"], "height": height_per_image}
        for i in range(num_images)
    ]
