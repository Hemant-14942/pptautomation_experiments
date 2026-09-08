"""Emit picture shapes from classified input items."""

from __future__ import annotations

import copy
import logging
from typing import Any

from lxml import etree

from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import q
from app.dynamic_rendering.utils.xml.shape_mutators import renumber_ids, strip_blip_ext_lst

logger = logging.getLogger(__name__)


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
    clone = copy.deepcopy(item["xml"])
    blip = clone.find(".//" + q("a:blip"))
    if blip is None:
        spTree.append(clone)
        return
    strip_blip_ext_lst(blip)

    image_bytes = item.get("image_bytes")
    if image_bytes is None:
        logger.warning("dropped picture with no resolvable source image")
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
