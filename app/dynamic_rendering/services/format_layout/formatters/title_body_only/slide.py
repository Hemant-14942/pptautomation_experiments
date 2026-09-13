"""Format one title_body_only slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.title_body_only.formatter import format_body_only
from app.dynamic_rendering.services.format_layout.formatters.title_body_only.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape
from app.dynamic_rendering.services.format_layout.shared.title_heading_slide import format_title_heading_shapes


def format_title_body_only_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide, prs)
    if shapes is None:
        return False

    slide_width = prs.slide_width if prs is not None else slide.part.presentation.slide_width
    format_title_heading_shapes(slide, slide_width)

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["body_el"], format_body_only(shapes["body_el"]))
    return True
