"""Fixed layout for question pill + question text + single image (no MCQ, no table)."""

from app.dynamic_rendering.services.format_layout.shared.qpill_layout import (
    QUESTION_PILL,
    question_pill_for,
)
from app.dynamic_rendering.services.format_layout.shared.title_content_layout import (
    BOTTOM_MARGIN_EMU,
    SLIDE_HEIGHT_EMU,
    SLIDE_WIDTH_EMU,
)

CONTENT_LEFT_EMU = 1_104_806
CONTENT_WIDTH_EMU = 34_747_200
PILL_TO_TEXT_GAP_EMU = 220_000
TEXT_HEIGHT_EMU = 3_500_000
TEXT_TO_IMAGE_GAP_EMU = 400_000

# Image box: ~80% slide width, centered under the question text.
IMAGE_AREA_WIDTH_EMU = int(0.8 * SLIDE_WIDTH_EMU)
IMAGE_AREA_X_EMU = (SLIDE_WIDTH_EMU - IMAGE_AREA_WIDTH_EMU) // 2

QUESTION_TEXT = {
    "x": CONTENT_LEFT_EMU,
    "y": QUESTION_PILL["y"] + QUESTION_PILL["height"] + PILL_TO_TEXT_GAP_EMU,
    "width": CONTENT_WIDTH_EMU,
    "height": TEXT_HEIGHT_EMU,
}


def question_text_for(dspec=None) -> dict:
    """Question text box below the (defence-aware) question pill."""
    pill = question_pill_for(dspec)
    y = pill["y"] + pill["height"] + PILL_TO_TEXT_GAP_EMU
    return {
        "x": CONTENT_LEFT_EMU,
        "y": y,
        "width": CONTENT_WIDTH_EMU,
        "height": TEXT_HEIGHT_EMU,
    }


def image_area_for(dspec=None) -> dict:
    """Image box below the question text, running down to the slide bottom margin.

    Defence-aware: question_text_for already shifts down when the template
    reserves a top banner, so this box follows automatically.
    """
    text = question_text_for(dspec)
    y = text["y"] + text["height"] + TEXT_TO_IMAGE_GAP_EMU
    bottom = SLIDE_HEIGHT_EMU - BOTTOM_MARGIN_EMU
    return {
        "x": IMAGE_AREA_X_EMU,
        "y": y,
        "width": IMAGE_AREA_WIDTH_EMU,
        "height": bottom - y,
    }
