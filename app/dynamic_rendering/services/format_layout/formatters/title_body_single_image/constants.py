"""Fixed textbox coordinates for the title_body_single_image slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    content_height_for,
    content_start_y_for,
)

BODY_TEXTBOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": 21_409_273,
    "height": content_height_for(CONTENT_START_Y),
}

IMAGE_TEXTBOX = {
    "x": 23_055_193,
    "y": 6_783_665,
    "width": 11_880_273,
    "height": 7_478_618,
}


def body_textbox_for(dspec=None) -> dict:
    y = content_start_y_for(dspec)
    return {
        "x": CONTENT_LEFT_X,
        "y": y,
        "width": 21_409_273,
        "height": content_height_for(y),
    }


def image_textbox_for(dspec=None) -> dict:
    y = content_start_y_for(dspec)
    return {
        "x": IMAGE_TEXTBOX["x"],
        "y": y,
        "width": IMAGE_TEXTBOX["width"],
        "height": content_height_for(y),
    }
