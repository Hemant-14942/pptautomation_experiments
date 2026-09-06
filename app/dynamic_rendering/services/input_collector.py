"""
Walk input deck slides and classify each shape into a role for emitters.

Roles: title_heading, heading, option, table, picture, body.
"""

from __future__ import annotations

import copy
from typing import Any

from pptx import Presentation

from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.classifiers.heading_adjust import (
    apply_detected_heading,
    detected_heading_for_slide,
)
from app.dynamic_rendering.services.classifiers.mcq_shapes import (
    classify_grouped_option,
    classify_mcq_heading,
    classify_standalone_option,
)
from app.dynamic_rendering.services.classifiers.media_shapes import (
    classify_graphic_frame,
    classify_picture,
    classify_title_banner,
)
from app.dynamic_rendering.utils.xml.helpers import local_name, off_ext, q


def collect_inputs(input_path: str, dspec: DesignSpec | None = None) -> list[dict[str, Any]]:
    """Per input slide: index + list of classified shape items."""
    prs = Presentation(input_path)
    slide_width, slide_height = prs.slide_width, prs.slide_height
    out: list[dict[str, Any]] = []

    for idx, slide in enumerate(prs.slides):
        sptree = slide._element.find(q("p:cSld") + "/" + q("p:spTree"))
        if sptree is None:
            out.append({"index": idx, "items": []})
            continue

        children = [c for c in list(sptree) if local_name(c) in {"sp", "pic", "grpSp", "graphicFrame"}]
        claimed: set = set()
        items: list[dict[str, Any]] = []

        for i, child in enumerate(children):
            if id(child) in claimed:
                continue
            tag = local_name(child)

            if tag == "sp":
                off, ext = off_ext(child, "p:spPr")

                if dspec is not None:
                    banner_item = classify_title_banner(
                        child, children, i, off, ext, claimed, dspec, slide_width, slide_height,
                    )
                    if banner_item is not None:
                        items.append(banner_item)
                        continue

                heading_item = classify_mcq_heading(child, children, i, off, ext, claimed)
                if heading_item is not None:
                    items.append(heading_item)
                    continue

                option_item = classify_standalone_option(child, children, i, off, ext, claimed)
                if option_item is not None:
                    items.append(option_item)
                    continue

                items.append({"kind": "body", "xml": copy.deepcopy(child)})

            elif tag == "grpSp":
                grouped = classify_grouped_option(child)
                if grouped is not None:
                    items.append(grouped)
                else:
                    items.append({"kind": "body", "xml": copy.deepcopy(child)})

            elif tag == "graphicFrame":
                items.append(classify_graphic_frame(child))

            elif tag == "pic":
                items.append(classify_picture(child, slide))

        heading = detected_heading_for_slide(slide, idx, prs)
        items = apply_detected_heading(items, heading, dspec, slide_width)
        out.append({"index": idx, "items": items})

    return out
