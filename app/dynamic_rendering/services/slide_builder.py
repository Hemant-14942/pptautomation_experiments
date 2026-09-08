"""Build one output slide from a template slide + classified input items."""

from __future__ import annotations

import copy
import re
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.presentation_defaults import FIRST_SHAPE_ID_PER_SLIDE
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.services.shape_emitters import (
    emit_body,
    emit_heading,
    emit_option,
    emit_picture,
    emit_title_heading,
)
from app.dynamic_rendering.services.table_restyle import restyle_table
from app.dynamic_rendering.utils.xml.helpers import q

PRES_RELS_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

# scrub_template_slide:
# - Deep-copies the template slide so the ORIGINAL template stays untouched
#   (needed because this runs once per output slide).
# - Removes all old shapes (text/images/tables) from the shape tree (spTree),
#   giving a clean/empty canvas to fill with new content.
# - Keeps nvGrpSpPr — it's a required PowerPoint tag, not a visible shape;
#   deleting it makes the file invalid/corrupt.
# - p:bg (background/theme) is NOT touched — it lives outside spTree,
#   so template's look & feel carries over automatically.

def scrub_template_slide(slide_xml: etree._Element) -> etree._Element:
    """Clone template slide XML but remove all shapes except nvGrpSpPr (keeps p:bg)."""
    fresh = copy.deepcopy(slide_xml)
    spTree = fresh.find(q("p:cSld") + "/" + q("p:spTree"))
    if spTree is None:
        return fresh
    nvGrpSpPr = spTree.find(q("p:nvGrpSpPr"))
    for child in list(spTree):
        if child is nvGrpSpPr:
            continue
        spTree.remove(child)
    return fresh


def sorted_slide_partnames(template_parts: dict[str, bytes]) -> list[str]:
    return sorted(
        [n for n in template_parts if re.match(r"ppt/slides/slide\d+\.xml$", n)],
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )


def layout_partname_for_slide(template_parts: dict[str, bytes], slide_name: str) -> str:
    rels_name = slide_name.replace("slides/", "slides/_rels/") + ".rels"
    if rels_name not in template_parts:
        return "ppt/slideLayouts/slideLayout1.xml"
    for rel in etree.fromstring(template_parts[rels_name]).iter():
        if rel.get("Type", "").endswith("/slideLayout"):
            target = rel.get("Target", "").lstrip("/")
            if target:
                return target if target.startswith("ppt/") else f"ppt/{target}"
    return "ppt/slideLayouts/slideLayout1.xml"


def build_slide(
    *,
    slide_index: int,
    info: dict[str, Any],
    tmpl_slide_xml: etree._Element,
    tmpl_layout_partname: str,
    tmpl_rels_blob: bytes | None,
    dspec: DesignSpec,
    out_parts: dict[str, bytes],
    pic_media_state: dict[str, int],
    title_icon_media_partname: str | None,
    used_layouts: dict[str, str],
    new_pres_rels: etree._Element,
) -> tuple[bytes, bytes]:
    """Build slide XML + slide rels for one input slide."""
    # this is the fresh slide free from al the old shapes,except the background,nvgrpsppr becoz have the metadata of the background
    fresh = scrub_template_slide(tmpl_slide_xml)
    spTree = fresh.find(q("p:cSld") + "/" + q("p:spTree"))
    # this is the relationships element for the slide, it contains the relationships for the slide
    slide_rels_xml = etree.Element(PRES_RELS_NS + "Relationships")
    # this is the id state for the shapes, it is used to generate the id for the new shapes,and preserve the id collision
    id_state = {"next": FIRST_SHAPE_ID_PER_SLIDE}

    for item in info["items"]:
        # this is the item, it is the item that is being rendered, it is a dictionary with the following keys:
        # - kind: the type of the item
        # - xml: the xml of the item
        # - dspec: the design specification for the item
        # - id_state: the id state for the item
        # - slide_rels_xml: the relationships element for the item
        # - PRES_RELS_NS: the namespace for the relationships element
        # - out_parts: the parts for the item
        kind = item["kind"]
        if kind == "heading":
            emit_heading(spTree, item, dspec, id_state)
        elif kind == "title_heading":
            emit_title_heading(
                spTree, item, dspec, id_state, slide_rels_xml, PRES_RELS_NS, title_icon_media_partname,
            )
        elif kind == "option":
            emit_option(spTree, item, dspec, id_state)
        elif kind == "table":
            tbl_el = copy.deepcopy(item["xml"])
            restyle_table(tbl_el, dspec)
            spTree.append(tbl_el)
        elif kind == "picture":
            emit_picture(
                spTree, item, dspec, id_state, slide_rels_xml, PRES_RELS_NS, out_parts, pic_media_state,
            )
        else:
            emit_body(spTree, item, dspec)

    layout_rid = used_layouts.get(tmpl_layout_partname)
    if layout_rid is None:
        layout_rid = f"rIdLayout{len(used_layouts) + 1}"
        used_layouts[tmpl_layout_partname] = layout_rid
        rel_el = etree.SubElement(new_pres_rels, PRES_RELS_NS + "Relationship")
        rel_el.set("Id", layout_rid)
        rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout")
        rel_el.set("Target", tmpl_layout_partname.replace("ppt/", ""))

    slide_rid = f"rId{slide_index + 100}"
    rel_el = etree.SubElement(new_pres_rels, PRES_RELS_NS + "Relationship")
    rel_el.set("Id", slide_rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide")
    rel_el.set("Target", f"slides/slide{slide_index + 1}.xml")

    rel_el2 = etree.SubElement(slide_rels_xml, PRES_RELS_NS + "Relationship")
    rel_el2.set("Id", layout_rid)
    rel_el2.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout")
    rel_el2.set("Target", tmpl_layout_partname.replace("ppt/", ""))

    if tmpl_rels_blob:
        tmpl_rels_root = etree.fromstring(tmpl_rels_blob)
        for rel in tmpl_rels_root:
            rtype = rel.get("Type", "")
            if rtype.endswith("/image"):
                image_rel = etree.SubElement(slide_rels_xml, PRES_RELS_NS + "Relationship")
                image_rel.set("Id", rel.get("Id"))
                image_rel.set("Type", rtype)
                image_rel.set("Target", rel.get("Target"))

    slide_bytes = etree.tostring(fresh, xml_declaration=True, encoding="UTF-8", standalone=True)
    rels_bytes = etree.tostring(slide_rels_xml, xml_declaration=True, encoding="UTF-8", standalone=True)
    return slide_bytes, rels_bytes
