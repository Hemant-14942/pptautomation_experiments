"""Fixed textbox coordinates for the title_body_only slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    BOTTOM_MARGIN_EMU,
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    CONTENT_WIDTH_EMU,
    SLIDE_HEIGHT_EMU,
)

BODY_TEXTBOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": CONTENT_WIDTH_EMU,
    "height": SLIDE_HEIGHT_EMU - CONTENT_START_Y - BOTTOM_MARGIN_EMU,
}
