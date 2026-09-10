"""Format one question_qtext_mcq slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.formatter import (
    format_mcq_answer_text,
    format_mcq_option_label,
    format_mcq_option_pill,
    format_question_label,
    format_question_pill,
    format_question_text,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_mcq.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape


def format_qpill_qtext_mcq_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide)
    if shapes is None:
        return False

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["question_pill_el"], format_question_pill(shapes["question_pill_el"]))
    replace_shape(sp_tree, shapes["question_label_el"], format_question_label(shapes["question_label_el"]))
    replace_shape(sp_tree, shapes["question_text_el"], format_question_text(shapes["question_text_el"]))

    letters = ["A", "B", "C", "D"]
    for opt_idx, pill_el in enumerate(shapes["mcq_pill_els"]):
        clone = format_mcq_option_pill(opt_idx, pill_el)
        if clone is not None:
            replace_shape(sp_tree, pill_el, clone)
            label_el = shapes["mcq_label_els"].get(letters[opt_idx])
            if label_el is not None:
                replace_shape(sp_tree, label_el, format_mcq_option_label(opt_idx, label_el))

        text_el = shapes["mcq_text_els"][opt_idx]
        replace_shape(sp_tree, text_el, format_mcq_answer_text(opt_idx, text_el))

    return True
