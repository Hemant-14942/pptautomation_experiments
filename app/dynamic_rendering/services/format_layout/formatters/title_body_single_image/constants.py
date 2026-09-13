"""Fixed textbox coordinates for the title_body_single_image slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    BOTTOM_MARGIN_EMU,
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    SLIDE_HEIGHT_EMU,
)

BODY_TEXTBOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": 21_409_273,
    "height": SLIDE_HEIGHT_EMU - CONTENT_START_Y - BOTTOM_MARGIN_EMU,
}

IMAGE_TEXTBOX = {
    "x": 23_055_193,
    "y": 6_783_665,
    "width": 11_880_273,
    "height": 7_478_618,
}
