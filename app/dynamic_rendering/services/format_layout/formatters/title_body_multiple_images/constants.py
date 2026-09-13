"""Fixed textbox coordinates for the title_body_multiple_images slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    BOTTOM_MARGIN_EMU,
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    SLIDE_HEIGHT_EMU,
    SLIDE_WIDTH_EMU,
)

BODY_TEXTBOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": 21_409_273,
    "height": SLIDE_HEIGHT_EMU - CONTENT_START_Y - BOTTOM_MARGIN_EMU,
}

IMAGE_AREA = {
    "x": BODY_TEXTBOX["x"] + BODY_TEXTBOX["width"],
    "y": BODY_TEXTBOX["y"],
    "width": SLIDE_WIDTH_EMU - (BODY_TEXTBOX["x"] + BODY_TEXTBOX["width"]),
    "height": SLIDE_HEIGHT_EMU - BODY_TEXTBOX["y"],
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
