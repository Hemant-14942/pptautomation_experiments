"""Fixed content-area box for the title_table_only slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    CONTENT_WIDTH_EMU,
    SLIDE_HEIGHT_EMU,
)

TABLE_BOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": CONTENT_WIDTH_EMU,
    "height": SLIDE_HEIGHT_EMU - CONTENT_START_Y,
}
