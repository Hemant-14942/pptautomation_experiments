"""Format title banner, icon, and label to fixed layout on input slides."""

from __future__ import annotations

from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.detection.title_slide_shapes import find_title_heading_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape
from app.dynamic_rendering.services.format_layout.shared.title_heading_layout import (
    format_title_banner,
    format_title_icon,
    format_title_label,
)


def format_title_heading_shapes(slide: Slide, slide_width: int) -> bool:
    shapes = find_title_heading_shapes(slide, slide_width)
    if shapes is None:
        return False

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["banner_el"], format_title_banner(shapes["banner_el"]))

    if shapes["icon_el"] is not None:
        replace_shape(sp_tree, shapes["icon_el"], format_title_icon(shapes["icon_el"]))

    if shapes["label_el"] is not None:
        replace_shape(sp_tree, shapes["label_el"], format_title_label(shapes["label_el"]))

    return True
