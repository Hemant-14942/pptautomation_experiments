"""Locate shapes on a qpill_qtext_image_mcq input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.mcq_slide_shapes import (
    find_mcq_slide_shapes,
)
from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import (
    IMAGE_Y_THRESHOLD_EMU,
)


def find_shapes(slide: Slide) -> dict | None:
    shapes = find_mcq_slide_shapes(slide)
    if shapes is None:
        return None

    pictures: list[tuple[int, int, object, tuple[int, int]]] = []
    for sp in slide.shapes:
        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "PICTURE":
            if sp.top is not None and sp.top > IMAGE_Y_THRESHOLD_EMU:
                pictures.append((sp.top, sp.left, sp._element, sp.image.size))

    if not pictures or len(pictures) > 2:
        return None

    pictures.sort(key=lambda item: (item[0], item[1]))

    mcq_options = shapes["mcq_options"]
    return {
        **shapes,
        "picture_els": [p[2] for p in pictures],
        "picture_sizes": [p[3] for p in pictures],
        "mcq_pill_els": [opt["pill_el"] for opt in mcq_options],
        "mcq_label_els": {
            opt["letter"]: opt["label_el"]
            for opt in mcq_options
            if opt["label_el"] is not None and not opt["grouped"]
        },
        "mcq_text_els": [opt["text_el"] for opt in mcq_options],
    }
