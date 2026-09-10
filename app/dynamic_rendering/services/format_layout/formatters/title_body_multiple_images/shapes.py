"""Locate body text and content pictures on a title_body_multiple_images slide."""

from __future__ import annotations

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import IMAGE_Y_THRESHOLD_EMU
from app.dynamic_rendering.services.format_layout.shared.shape_finders import find_body_el


def find_shapes(slide: Slide, prs: Presentation | None = None) -> dict | None:
    body_el = find_body_el(slide, prs)

    pictures: list[tuple[int, int, object, tuple[int, int]]] = []
    for sp in slide.shapes:
        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "PICTURE":
            if sp.top is not None and sp.top > IMAGE_Y_THRESHOLD_EMU:
                pictures.append((sp.top, sp.left, sp._element, sp.image.size))

    if body_el is None or not pictures:
        return None

    pictures.sort(key=lambda item: (item[0], item[1]))
    return {
        "body_el": body_el,
        "picture_els": [p[2] for p in pictures],
        "image_sizes": [p[3] for p in pictures],
    }
