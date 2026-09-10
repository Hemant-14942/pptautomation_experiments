"""Fixed image layout for title_image_only slides.

Heading pill stays in place (not repositioned). Content images live in the
area below the heading pill with 2-inch left/right margins — same grid rules
as image_only (1=centered, 2=left|right, 3=2+1, 4=2x2, 5+=auto grid).

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches).
"""

from app.core.fit_layout.layout_formatter.image_only.constants import (
    IMAGE_GAP_EMU,
    INCH_EMU,
    SIDE_MARGIN_EMU,
    SLIDE_HEIGHT_EMU,
    SLIDE_WIDTH_EMU,
    get_image_boxes,
)

# Content starts below heading pill (same top as title_body_only / title_table_only)
CONTENT_TOP_EMU = 4_711_025  # 5.151 inches

CONTENT_AREA = {
    "x": SIDE_MARGIN_EMU,
    "y": CONTENT_TOP_EMU,
    "width": SLIDE_WIDTH_EMU - 2 * SIDE_MARGIN_EMU,
    "height": SLIDE_HEIGHT_EMU - CONTENT_TOP_EMU - SIDE_MARGIN_EMU,
}


def get_title_image_boxes(num_images: int, layout: str = "balanced") -> list[dict[str, int]]:
    """Return image slot boxes below the heading pill."""
    return get_image_boxes(num_images, layout=layout, content_area=CONTENT_AREA)
