"""Shared content-area geometry for all title slide types.

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches). 1 inch = 914,400 EMU.
"""

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 36_576_000
SLIDE_HEIGHT_EMU = 20_574_000

CONTENT_LEFT_X = INCH_EMU
# Legacy standard-red body top (prefer content_start_y_for when dspec is available).
CONTENT_START_Y = 4_711_025
BOTTOM_MARGIN_EMU = INCH_EMU

# Full-width body/table area below the title heading (80% slide width).
CONTENT_WIDTH_EMU = 29_260_560

# Long bullet lists use top anchor + normAutofit; shorter lists stay vertically centered.
BODY_LONG_LIST_PARAGRAPH_THRESHOLD = 10


def content_start_y_for(dspec=None) -> int:
    """Y coordinate for body/images: bottom of title banner or icon, whichever is lower."""
    from app.dynamic_rendering.services.format_layout.shared.title_heading_layout import (
        fixed_title_heading_geometry,
    )

    geo = fixed_title_heading_geometry(dspec)
    banner_bottom = geo["banner_off"][1] + geo["banner_ext"][1]
    icon_bottom = geo["icon_off"][1] + geo["icon_ext"][1]
    return max(banner_bottom, icon_bottom)


def content_height_for(y: int) -> int:
    """Height from content top y down to the slide bottom margin."""
    return SLIDE_HEIGHT_EMU - y - BOTTOM_MARGIN_EMU
