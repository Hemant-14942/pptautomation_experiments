"""Format one title_body_multiple_images slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.title_body_multiple_images.formatter import (
    format_body,
    format_images,
)
from app.dynamic_rendering.services.format_layout.formatters.title_body_multiple_images.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape


def format_title_body_multiple_images_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide, prs)
    if shapes is None:
        return False

    sp_tree = slide.shapes._spTree
    replace_shape(sp_tree, shapes["body_el"], format_body(shapes["body_el"]))

    clones = format_images(shapes["picture_els"], shapes["image_sizes"])
    for orig_el, clone_el in zip(shapes["picture_els"], clones):
        replace_shape(sp_tree, orig_el, clone_el)
    return True
