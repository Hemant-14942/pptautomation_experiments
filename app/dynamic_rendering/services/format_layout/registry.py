"""Map detected slide types to in-place layout formatters."""

from __future__ import annotations

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import (
    SLIDE_TYPE_BODY_ONLY,
    SLIDE_TYPE_IMAGE_ONLY,
    SLIDE_TYPE_QUESTION_QTEXT_MCQ,
    SLIDE_TYPE_QPILL_QTEXT_IMAGE_MCQ,
    SLIDE_TYPE_QPILL_QTEXT_ONLY,
    SLIDE_TYPE_QPILL_QTEXT_TABLE_MCQ,
    SLIDE_TYPE_TABLE_ONLY,
    SLIDE_TYPE_TITLE_BODY_MULTIPLE_IMAGES,
    SLIDE_TYPE_TITLE_BODY_ONLY,
    SLIDE_TYPE_TITLE_BODY_SINGLE_IMAGE,
    SLIDE_TYPE_TITLE_IMAGE_ONLY,
    SLIDE_TYPE_TITLE_TABLE_ONLY,
)
from app.dynamic_rendering.services.format_layout.formatters.body_only.slide import (
    format_body_only_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.image_only.slide import (
    format_image_only_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_image_mcq.slide import (
    format_qpill_qtext_image_mcq_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.slide import (
    format_qpill_qtext_mcq_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_only.slide import (
    format_qpill_qtext_only_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_table_mcq.slide import (
    format_qpill_qtext_table_mcq_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.table_only.slide import (
    format_table_only_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.title_body_multiple_images.slide import (
    format_title_body_multiple_images_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.title_body_only.slide import (
    format_title_body_only_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.title_body_single_image.slide import (
    format_title_body_single_image_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.title_image_only.slide import (
    format_title_image_only_slide,
)
from app.dynamic_rendering.services.format_layout.formatters.title_table_only.slide import (
    format_title_table_only_slide,
)

SLIDE_FORMATTERS: dict[str, object] = {
    SLIDE_TYPE_BODY_ONLY: format_body_only_slide,
    SLIDE_TYPE_IMAGE_ONLY: format_image_only_slide,
    SLIDE_TYPE_TABLE_ONLY: format_table_only_slide,
    SLIDE_TYPE_TITLE_BODY_ONLY: format_title_body_only_slide,
    SLIDE_TYPE_TITLE_TABLE_ONLY: format_title_table_only_slide,
    SLIDE_TYPE_TITLE_BODY_SINGLE_IMAGE: format_title_body_single_image_slide,
    SLIDE_TYPE_TITLE_BODY_MULTIPLE_IMAGES: format_title_body_multiple_images_slide,
    SLIDE_TYPE_TITLE_IMAGE_ONLY: format_title_image_only_slide,
    SLIDE_TYPE_QPILL_QTEXT_ONLY: format_qpill_qtext_only_slide,
    SLIDE_TYPE_QUESTION_QTEXT_MCQ: format_qpill_qtext_mcq_slide,
    SLIDE_TYPE_QPILL_QTEXT_TABLE_MCQ: format_qpill_qtext_table_mcq_slide,
    SLIDE_TYPE_QPILL_QTEXT_IMAGE_MCQ: format_qpill_qtext_image_mcq_slide,
}


def format_slide(slide: Slide, slide_type: str, prs: Presentation | None = None) -> bool:
    """Apply layout formatter for slide_type. Returns False if unknown or shapes missing."""
    formatter = SLIDE_FORMATTERS.get(slide_type)
    if formatter is None:
        return False
    return bool(formatter(slide, prs))
