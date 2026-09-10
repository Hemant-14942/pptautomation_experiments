"""Locate the table shape on a title_table_only input slide."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.shared.shape_finders import find_table_el


def find_shapes(slide: Slide) -> dict | None:
    table_el = find_table_el(slide)
    if table_el is None:
        return None
    return {"table_el": table_el}
