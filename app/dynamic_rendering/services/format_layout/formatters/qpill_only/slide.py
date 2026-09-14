"""Format one qpill_only slide in place (question pill + label, no body text)."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.qpill_only.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.qpill_formatters import (
    format_question_label,
    format_question_pill,
)
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape


def format_qpill_only_slide(slide: Slide, prs: Presentation | None = None, dspec=None) -> bool:
    shapes = find_shapes(slide)
    if shapes is None:
        return False

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["question_pill_el"], format_question_pill(shapes["question_pill_el"], dspec))
    replace_shape(
        sp_tree,
        shapes["question_label_el"],
        format_question_label(shapes["question_label_el"], dspec=dspec),
    )
    return True
