"""Locate body text and one content picture on a title_body_single_image slide."""

from __future__ import annotations

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import IMAGE_Y_THRESHOLD_EMU
from app.dynamic_rendering.services.format_layout.shared.shape_finders import find_body_el


def find_shapes(slide: Slide, prs: Presentation | None = None) -> dict | None:
    body_el = find_body_el(slide, prs)
    picture_el = None
    picture_size = None

    for sp in slide.shapes:
        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "PICTURE":
            if sp.top is not None and sp.top > IMAGE_Y_THRESHOLD_EMU:
                picture_el = sp._element
                picture_size = sp.image.size

    if body_el is None or picture_el is None or picture_size is None:
        return None

    return {
        "body_el": body_el,
        "picture_el": picture_el,
        "picture_size": picture_size,
    }
