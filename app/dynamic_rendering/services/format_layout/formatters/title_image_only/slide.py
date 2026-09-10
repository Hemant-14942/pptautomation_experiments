"""Format one title_image_only slide in place."""

from pptx.presentation import Presentation
from pptx.slide import Slide

from app.dynamic_rendering.services.format_layout.formatters.title_image_only.formatter import format_images
from app.dynamic_rendering.services.format_layout.formatters.title_image_only.shapes import find_shapes
from app.dynamic_rendering.services.format_layout.shared.slide_tree import replace_shape


def format_title_image_only_slide(slide: Slide, prs: Presentation | None = None) -> bool:
    shapes = find_shapes(slide)
    if shapes is None:
        return False

    clones = format_images(shapes["picture_els"], shapes["image_sizes"])
    sp_tree = slide.shapes._spTree
    for orig_el, clone_el in zip(shapes["picture_els"], clones):
        replace_shape(sp_tree, orig_el, clone_el)
    return True
