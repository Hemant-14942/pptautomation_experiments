"""Format one qpill_qtext_table_mcq slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_table_mcq.formatter import (
    format_mcq_answer_text,
    format_mcq_option_label,
    format_mcq_option_pill,
    format_question_label,
    format_question_pill,
    format_question_text,
    format_table,
)
from app.dynamic_rendering.services.format_layout.formatters.qpill_qtext_table_mcq.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape


def format_qpill_qtext_table_mcq_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide)
    if shapes is None:
        return False

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["question_pill_el"], format_question_pill(shapes["question_pill_el"]))
    replace_shape(sp_tree, shapes["question_label_el"], format_question_label(shapes["question_label_el"]))
    replace_shape(sp_tree, shapes["question_text_el"], format_question_text(shapes["question_text_el"]))
    replace_shape(sp_tree, shapes["table_el"], format_table(shapes["table_el"]))

    for opt in shapes["mcq_options"]:
        opt_idx = opt["option_idx"]
        pill_el = opt["pill_el"]
        clone = format_mcq_option_pill(opt_idx, pill_el)
        if clone is not None:
            replace_shape(sp_tree, pill_el, clone)
            label_el = opt["label_el"]
            if label_el is not None and not opt["grouped"]:
                replace_shape(sp_tree, label_el, format_mcq_option_label(opt_idx, label_el))

        replace_shape(sp_tree, opt["text_el"], format_mcq_answer_text(opt_idx, opt["text_el"]))

    return True
