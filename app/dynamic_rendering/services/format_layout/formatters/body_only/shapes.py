"""Locate the body text shape on a body_only input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.shared.shape_finders import find_body_only_el


def find_shapes(slide: Slide) -> dict | None:
    body_el = find_body_only_el(slide)
    if body_el is None:
        return None
    return {"body_el": body_el}
