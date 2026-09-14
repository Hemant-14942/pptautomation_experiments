"""Fixed content-area box for the title_table_only slide type."""

from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    CONTENT_WIDTH_EMU,
    SLIDE_HEIGHT_EMU,
)

EXTRA_Y_OFFSET_EMU_FOR_DEFENCE = 2_165_995

TABLE_BOX = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": CONTENT_WIDTH_EMU,
    "height": SLIDE_HEIGHT_EMU - CONTENT_START_Y,
}


def table_box_for(dspec=None) -> dict:
    y = CONTENT_START_Y
    if dspec is not None and dspec.has_top_banner():
        y += EXTRA_Y_OFFSET_EMU_FOR_DEFENCE
    return {
        "x": CONTENT_LEFT_X,
        "y": y,
        "width": CONTENT_WIDTH_EMU,
        "height": SLIDE_HEIGHT_EMU - y,
    }
