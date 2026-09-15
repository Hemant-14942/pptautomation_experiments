"""Fixed layout for question pill + text + image + MCQ slides."""

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
    MCQ_OPTIONS as _BASE_MCQ_OPTIONS,
    QUESTION_LABEL,
    QUESTION_PILL,
    QUESTION_TEXT,
)

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 40 * INCH_EMU
HALF_SLIDE_EMU = SLIDE_WIDTH_EMU // 2
COLUMN_GAP_EMU = int(0.2 * INCH_EMU)
CONTENT_LEFT_EMU = 1_104_806
ANSWER_TEXT_X = 3_107_605
LEFT_ANSWER_WIDTH_EMU = HALF_SLIDE_EMU - ANSWER_TEXT_X - COLUMN_GAP_EMU

_MCQ_ZONE_TOP = _BASE_MCQ_OPTIONS[0]["pill"]["y"]
_LAST_PILL = _BASE_MCQ_OPTIONS[3]["pill"]
_MCQ_ZONE_BOTTOM = _LAST_PILL["y"] + _LAST_PILL["height"]

IMAGE_BOX = {
    "x": HALF_SLIDE_EMU + COLUMN_GAP_EMU,
    "y": _MCQ_ZONE_TOP,
    "width": SLIDE_WIDTH_EMU - (HALF_SLIDE_EMU + COLUMN_GAP_EMU) - CONTENT_LEFT_EMU,
    "height": _MCQ_ZONE_BOTTOM - _MCQ_ZONE_TOP + int(0.5 * INCH_EMU),
}


def image_box_for(dspec=None) -> dict[str, int]:
    """Right-column image box aligned with the MCQ option zone (defence-aware)."""
    from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.constants import (
        mcq_options_for,
    )

    options = mcq_options_for(dspec)
    zone_top = options[0]["pill"]["y"]
    last_pill = options[3]["pill"]
    zone_bottom = last_pill["y"] + last_pill["height"]
    return {
        "x": IMAGE_BOX["x"],
        "y": zone_top,
        "width": IMAGE_BOX["width"],
        "height": zone_bottom - zone_top + int(0.5 * INCH_EMU),
    }


def image_boxes_for(num_images: int, dspec=None) -> list[dict[str, int]]:
    """Per-image boxes inside the reserved right column.

    One image fills the whole column (same as image_box_for). Two images
    are stacked vertically, each taking 45% of the column height with a
    5% gap between them, mirroring title_body_multiple_images.
    """
    area = image_box_for(dspec)
    if num_images <= 1:
        return [area]

    height_per_image = round(area["height"] * 0.45)
    gap = round(area["height"] * 0.05)
    return [
        {"x": area["x"], "y": area["y"], "width": area["width"], "height": height_per_image},
        {
            "x": area["x"],
            "y": area["y"] + height_per_image + gap,
            "width": area["width"],
            "height": height_per_image,
        },
    ]
