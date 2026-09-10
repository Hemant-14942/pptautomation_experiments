"""Format one qpill_qtext_only slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_only.formatter import (
    format_question_label,
    format_question_pill,
    format_question_text,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_only.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape


def format_qpill_qtext_only_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide)
    if shapes is None:
        return False

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["question_pill_el"], format_question_pill(shapes["question_pill_el"]))
    replace_shape(sp_tree, shapes["question_label_el"], format_question_label(shapes["question_label_el"]))
    replace_shape(sp_tree, shapes["question_text_el"], format_question_text(shapes["question_text_el"]))
    return True
