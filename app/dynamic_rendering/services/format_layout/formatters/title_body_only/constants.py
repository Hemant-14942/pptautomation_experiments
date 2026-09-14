"""Fixed textbox coordinates for the title_body_only slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    CONTENT_WIDTH_EMU,
    content_height_for,
    content_start_y_for,
)

BODY_TEXTBOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": CONTENT_WIDTH_EMU,
    "height": content_height_for(CONTENT_START_Y),
}


def body_textbox_for(dspec=None) -> dict:
    y = content_start_y_for(dspec)
    return {
        "x": CONTENT_LEFT_X,
        "y": y,
        "width": CONTENT_WIDTH_EMU,
        "height": content_height_for(y),
    }
