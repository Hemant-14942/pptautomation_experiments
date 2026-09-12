"""Locate shapes on a question_qtext_mcq input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.mcq_slide_shapes import (
    find_mcq_slide_shapes,
)


def find_shapes(slide: Slide) -> dict | None:
    shapes = find_mcq_slide_shapes(slide)
    if shapes is None:
        return None

    mcq_options = shapes["mcq_options"]
    return {
        **shapes,
        "mcq_pill_els": [opt["pill_el"] for opt in mcq_options],
        "mcq_label_els": {
            opt["letter"]: opt["label_el"]
            for opt in mcq_options
            if opt["label_el"] is not None and not opt["grouped"]
        },
        "mcq_text_els": [opt["text_el"] for opt in mcq_options],
    }
