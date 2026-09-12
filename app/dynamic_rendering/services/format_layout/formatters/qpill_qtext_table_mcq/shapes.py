"""Locate shapes on a qpill_qtext_table_mcq input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.mcq_slide_shapes import (
    find_mcq_slide_shapes,
)


def find_shapes(slide: Slide) -> dict | None:
    shapes = find_mcq_slide_shapes(slide)
    if shapes is None:
        return None

    table_el = None
    for sp in slide.shapes:
        if sp.has_table:
            table_el = sp._element
            break
    if table_el is None:
        return None

    mcq_options = shapes["mcq_options"]
    return {
        **shapes,
        "table_el": table_el,
        "mcq_pill_els": [opt["pill_el"] for opt in mcq_options],
        "mcq_label_els": {
            opt["letter"]: opt["label_el"]
            for opt in mcq_options
            if opt["label_el"] is not None and not opt["grouped"]
        },
        "mcq_text_els": [opt["text_el"] for opt in mcq_options],
    }
