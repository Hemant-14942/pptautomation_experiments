"""Locate the body text shape on a title_body_only input slide."""

from __future__ import annotations

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.shared.shape_finders import find_body_el


def find_shapes(slide: Slide, prs: Presentation | None = None) -> dict | None:
    body_el = find_body_el(slide, prs)
    if body_el is None:
        return None
    return {"body_el": body_el}
