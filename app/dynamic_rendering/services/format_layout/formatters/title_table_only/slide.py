"""Format one title_table_only slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.title_table_only.formatter import format_table
from app.dynamic_rendering.services.format_layout.formatters.title_table_only.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape
from app.dynamic_rendering.services.format_layout.shared.title_heading_slide import format_title_heading_shapes


def format_title_table_only_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide)
    if shapes is None:
        return False

    slide_width = prs.slide_width if prs is not None else slide.part.presentation.slide_width
    format_title_heading_shapes(slide, slide_width)

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["table_el"], format_table(shapes["table_el"]))
    return True
