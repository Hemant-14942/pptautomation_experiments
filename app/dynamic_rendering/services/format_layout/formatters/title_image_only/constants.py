"""Fixed image layout for title_image_only slides."""

from app.dynamic_rendering.services.format_layout.formatters.image_only.constants import (
    SIDE_MARGIN_EMU,
    get_image_boxes,
)
from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    CONTENT_LEFT_X,
    CONTENT_START_Y,
    SLIDE_HEIGHT_EMU,
    SLIDE_WIDTH_EMU,
)

CONTENT_AREA = {
    "x": CONTENT_LEFT_X,
    "y": CONTENT_START_Y,
    "width": SLIDE_WIDTH_EMU - 2 * SIDE_MARGIN_EMU,
    "height": SLIDE_HEIGHT_EMU - CONTENT_START_Y - SIDE_MARGIN_EMU,
}


def get_title_image_boxes(num_images: int, layout: str = "balanced") -> list[dict[str, int]]:
    return get_image_boxes(num_images, layout=layout, content_area=CONTENT_AREA)
