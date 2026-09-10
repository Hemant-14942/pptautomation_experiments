"""Locate content pictures on an image_only input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import IMAGE_Y_THRESHOLD_EMU


def find_shapes(slide: Slide) -> dict | None:
    pictures: list[tuple[int, int, object, tuple[int, int]]] = []
    for sp in slide.shapes:
        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "PICTURE":
            if sp.top is not None and sp.top > IMAGE_Y_THRESHOLD_EMU:
                pictures.append((sp.top, sp.left, sp._element, sp.image.size))

    if not pictures:
        return None

    pictures.sort(key=lambda item: (item[0], item[1]))
    return {
        "picture_els": [p[2] for p in pictures],
        "image_sizes": [p[3] for p in pictures],
    }
