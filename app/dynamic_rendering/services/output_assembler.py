"""
Assemble the output .pptx zip parts in memory.

Copies the template archive, rebuilds slides from the output shell slide, and
rewrites presentation.xml, presentation rels, and [Content_Types].xml.
"""

from __future__ import annotations

import re
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.presentation_defaults import (
    DEFAULT_SLIDE_HEIGHT,
    DEFAULT_SLIDE_WIDTH,
    FIRST_SLIDE_ID,
)
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.content_types import update_content_types
from app.dynamic_rendering.services.presentation_xml import (
    build_presentation_xml,
    extract_int_attr,
    extract_notes_size,
)
from app.dynamic_rendering.services.slide_builder import (
    PRES_RELS_NS,
    build_slide,
    layout_partname_for_slide,
)

_SKIP_PART_PATTERNS = (
    re.compile(r"ppt/slides/slide\d+\.xml$"),
    re.compile(r"ppt/slides/_rels/slide\d+\.xml\.rels$"),
    re.compile(r"ppt/presentation\.xml$"),
    re.compile(r"ppt/_rels/presentation\.xml\.rels$"),
    re.compile(r"ppt/notesSlides/notesSlide\d+\.xml$"),
    re.compile(r"ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels$"),
)


def _should_skip_part(name: str) -> bool:
    return any(p.match(name) for p in _SKIP_PART_PATTERNS)

# any media file which is present in the design spec will be placed in first media folder in output zip
def _seed_design_spec_media(out_parts: dict[str, bytes], dspec: DesignSpec) -> str | None:
    title_icon_media_partname: str | None = None
    if dspec.title_icon_el is not None and dspec.title_icon_image_bytes is not None:
        ext = dspec.title_icon_image_ext or "png"
        title_icon_media_partname = f"ppt/media/design_spec_title_icon.{ext}"
        out_parts[title_icon_media_partname] = dspec.title_icon_image_bytes

    return title_icon_media_partname


def build_output(
    template_parts: dict[str, bytes],
    output_shell_xml: etree._Element,
    output_shell_partname: str,
    inputs: list[dict[str, Any]],
    dspec: DesignSpec,
) -> dict[str, bytes]:
    """Build the output zip parts (in-memory)."""
    out_parts: dict[str, bytes] = {
        name: blob for name, blob in template_parts.items() if not _should_skip_part(name)
    }

    title_icon_media_partname = _seed_design_spec_media(
        out_parts, dspec,
    )
    pic_media_state = {"next": 0}
    n = len(inputs)

    tmpl_pres_rels_blob = template_parts.get("ppt/_rels/presentation.xml.rels")
    if tmpl_pres_rels_blob:
        new_pres_rels = etree.fromstring(tmpl_pres_rels_blob)
        for rel in list(new_pres_rels):
            if rel.get("Type", "").endswith("/slide"):
                new_pres_rels.remove(rel)
    else:
        new_pres_rels = etree.Element(PRES_RELS_NS + "Relationships")

    tmpl_layout_partname = layout_partname_for_slide(template_parts, output_shell_partname)
    tmpl_rels_name = output_shell_partname.replace("slides/", "slides/_rels/") + ".rels"
    tmpl_rels_blob = template_parts.get(tmpl_rels_name)

    used_layouts: dict[str, str] = {}
    for i, info in enumerate(inputs):
        slide_bytes, rels_bytes = build_slide(
            slide_index=i,
            info=info,
            tmpl_slide_xml=output_shell_xml,
            tmpl_layout_partname=tmpl_layout_partname,
            tmpl_rels_blob=tmpl_rels_blob,
            dspec=dspec,
            out_parts=out_parts,
            pic_media_state=pic_media_state,
            title_icon_media_partname=title_icon_media_partname,
            used_layouts=used_layouts,
            new_pres_rels=new_pres_rels,
        )
        out_parts[f"ppt/slides/slide{i+1}.xml"] = slide_bytes
        out_parts[f"ppt/slides/_rels/slide{i+1}.xml.rels"] = rels_bytes

    pres_blob = template_parts.get("ppt/presentation.xml", b"")
    pres_xml = build_presentation_xml(
        n,
        start_id=FIRST_SLIDE_ID,
        slide_width=extract_int_attr(pres_blob, "p:sldSz", "cx", DEFAULT_SLIDE_WIDTH),
        slide_height=extract_int_attr(pres_blob, "p:sldSz", "cy", DEFAULT_SLIDE_HEIGHT),
        notes_size=extract_notes_size(pres_blob),
        base_pres_xml=pres_blob or None,
    )
    out_parts["ppt/presentation.xml"] = etree.tostring(
        pres_xml, xml_declaration=True, encoding="UTF-8", standalone=True,
    )
    out_parts["ppt/_rels/presentation.xml.rels"] = etree.tostring(
        new_pres_rels, xml_declaration=True, encoding="UTF-8", standalone=True,
    )

    if "[Content_Types].xml" in out_parts:
        out_parts["[Content_Types].xml"] = update_content_types(out_parts["[Content_Types].xml"], n, out_parts)

    return out_parts
