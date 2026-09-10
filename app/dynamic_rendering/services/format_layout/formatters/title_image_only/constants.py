"""Fixed image layout for title_image_only slides."""

from app.dynamic_rendering.services.format_layout.formatters.image_only.constants import (
    SIDE_MARGIN_EMU,
    SLIDE_HEIGHT_EMU,
    SLIDE_WIDTH_EMU,
    get_image_boxes,
)

CONTENT_TOP_EMU = 4_711_025

CONTENT_AREA = {
    "x": SIDE_MARGIN_EMU,
    "y": CONTENT_TOP_EMU,
    "width": SLIDE_WIDTH_EMU - 2 * SIDE_MARGIN_EMU,
    "height": SLIDE_HEIGHT_EMU - CONTENT_TOP_EMU - SIDE_MARGIN_EMU,
}


def get_title_image_boxes(num_images: int, layout: str = "balanced") -> list[dict[str, int]]:
    return get_image_boxes(num_images, layout=layout, content_area=CONTENT_AREA)
