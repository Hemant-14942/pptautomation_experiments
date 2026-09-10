"""Locate shapes on a qpill_qtext_table_mcq input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import (
    find_mcq_answer_text_elements,
    find_question_text_element,
    is_group,
)
from app.dynamic_rendering.utils.xml.helpers import prst_geom


def find_shapes(slide: Slide) -> dict | None:
    question_pill_el = None
    question_label_el = None
    table_el = None
    mcq_pill_els: list = []
    mcq_label_els: dict = {}

    for sp in slide.shapes:
        elem = sp._element

        if sp.has_table:
            table_el = elem
            continue

        if is_group(elem):
            mcq_pill_els.append(elem)
            continue

        geom = prst_geom(elem)
        if geom == "roundRect" and question_pill_el is None:
            question_pill_el = elem
            continue
        if geom == "ellipse":
            mcq_pill_els.append(elem)
            continue

        if not sp.has_text_frame:
            continue
        text = sp.text_frame.text.strip()
        if not text:
            continue

        if text == "Question" and question_label_el is None:
            question_label_el = elem
        elif text in ("A", "B", "C", "D") and text not in mcq_label_els:
            mcq_label_els[text] = elem

    question_text_el = find_question_text_element(slide, use_mcq_ceiling=True)
    mcq_text_els = (
        find_mcq_answer_text_elements(slide, question_text_el)
        if question_text_el is not None
        else []
    )

    if not (
        question_pill_el is not None
        and question_label_el is not None
        and question_text_el is not None
        and table_el is not None
        and len(mcq_pill_els) >= 4
        and len(mcq_text_els) >= 4
    ):
        return None

    return {
        "question_pill_el": question_pill_el,
        "question_label_el": question_label_el,
        "question_text_el": question_text_el,
        "table_el": table_el,
        "mcq_pill_els": mcq_pill_els[:4],
        "mcq_label_els": mcq_label_els,
        "mcq_text_els": mcq_text_els[:4],
    }
