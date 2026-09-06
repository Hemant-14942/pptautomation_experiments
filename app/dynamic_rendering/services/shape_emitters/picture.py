"""Emit picture shapes and skip logo duplicates."""

from __future__ import annotations

import copy
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import (
    LOGO_DUPLICATE_POSITION_TOLERANCE,
    LOGO_DUPLICATE_SIZE_TOLERANCE,
)
from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import renumber_ids, rects_close, strip_blip_ext_lst


def _looks_like_logo_duplicate(item: dict[str, Any], dspec: DesignSpec) -> bool:
    if dspec.logo_el is None or dspec.logo_ext is None:
        return False
    ext = item.get("ext")
    if not ext:
        return False
    return rects_close(
        item.get("off") or (0, 0),
        ext,
        item.get("off") or (0, 0),
        dspec.logo_ext,
        tol=LOGO_DUPLICATE_POSITION_TOLERANCE,
    ) and abs(ext[0] - dspec.logo_ext[0]) < LOGO_DUPLICATE_SIZE_TOLERANCE and abs(
        ext[1] - dspec.logo_ext[1]
    ) < LOGO_DUPLICATE_SIZE_TOLERANCE


def emit_picture(
    spTree: etree._Element,
    item: dict[str, Any],
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    out_parts: dict[str, bytes],
    pic_media_state: dict[str, int],
) -> None:
    if _looks_like_logo_duplicate(item, dspec):
        return

    clone = copy.deepcopy(item["xml"])
    blip = clone.find(".//" + q("a:blip"))
    if blip is None:
        spTree.append(clone)
        return
    strip_blip_ext_lst(blip)

    image_bytes = item.get("image_bytes")
    if image_bytes is None:
        print("[builder] warning: dropped a picture with no resolvable source image")
        return

    pic_media_state["next"] += 1
    ext = item.get("image_ext") or "png"
    partname = f"ppt/media/input_pic_{pic_media_state['next']}.{ext}"
    out_parts[partname] = image_bytes

    rid = f"rIdPic{id_state['next'] + 1}"
    blip.set("{%s}embed" % R, rid)
    renumber_ids(clone, id_state)
    spTree.append(clone)

    rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", "../media/" + partname.rsplit("/", 1)[-1])
