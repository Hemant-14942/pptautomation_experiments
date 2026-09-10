"""Locate shapes on a qpill_qtext_image_mcq input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.qpill_shape_utils import (
    find_mcq_answer_text_elements,
    find_question_text_element,
    is_group,
)
from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import IMAGE_Y_THRESHOLD_EMU
from app.dynamic_rendering.utils.xml.helpers import prst_geom


def find_shapes(slide: Slide) -> dict | None:
    question_pill_el = None
    question_label_el = None
    mcq_pill_els: list[tuple[int, object]] = []
    mcq_label_els: dict = {}
    picture_el = None
    picture_size = None

    for sp in slide.shapes:
        elem = sp._element

        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "PICTURE":
            if sp.top is not None and sp.top > IMAGE_Y_THRESHOLD_EMU:
                picture_el = elem
                picture_size = sp.image.size
            continue

        geom = prst_geom(elem)
        if geom == "roundRect" and question_pill_el is None:
            question_pill_el = elem
            continue
        if is_group(elem) or geom == "ellipse":
            mcq_pill_els.append((sp.top, elem))
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

    sorted_pills = [el for _, el in sorted(mcq_pill_els, key=lambda item: item[0])]

    if not (
        question_pill_el is not None
        and question_label_el is not None
        and question_text_el is not None
        and picture_el is not None
        and picture_size is not None
        and len(sorted_pills) >= 4
        and len(mcq_text_els) >= 4
    ):
        return None

    return {
        "question_pill_el": question_pill_el,
        "question_label_el": question_label_el,
        "question_text_el": question_text_el,
        "picture_el": picture_el,
        "picture_size": picture_size,
        "mcq_pill_els": sorted_pills[:4],
        "mcq_label_els": mcq_label_els,
        "mcq_text_els": mcq_text_els[:4],
    }
