"""Emit logo and question-icon branding shapes."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.constants.shape_geometry import LOGO_RECLONE_TOLERANCE
from app.dynamic_rendering.constants.xml_namespaces import R
from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.utils.xml.helpers import off_ext, q
from app.dynamic_rendering.utils.xml.shape_mutators import (
    clone_and_place,
    renumber_ids,
    rects_close,
    strip_blip_ext_lst,
)


def emit_question_icon(
    spTree: etree._Element,
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    question_icon_media_partname: str | None,
) -> None:
    """MCQ '?' badge — only for slides that have a Question pill."""
    if dspec.question_icon_el is None or question_icon_media_partname is None:
        return
    clone = clone_and_place(dspec.question_icon_el, dspec.question_icon_off, dspec.question_icon_ext)
    blip = clone.find(".//" + q("a:blip"))
    if blip is None:
        return
    strip_blip_ext_lst(blip)
    rid = f"rIdQuestionIcon{id_state['next'] + 1}"
    blip.set("{%s}embed" % R, rid)
    renumber_ids(clone, id_state)
    spTree.append(clone)
    rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", "../" + question_icon_media_partname.replace("ppt/", ""))


def emit_logo(
    spTree: etree._Element,
    dspec: DesignSpec,
    id_state: dict[str, int],
    slide_rels_xml: etree._Element,
    pres_rels_ns: str,
    logo_media_partname: str | None,
) -> None:
    if dspec.logo_el is None or logo_media_partname is None:
        return
    for existing in spTree.iter(q("p:pic")):
        off, ext = off_ext(existing, "p:spPr")
        if rects_close(off, ext, dspec.logo_off, dspec.logo_ext, tol=LOGO_RECLONE_TOLERANCE):
            return
    clone = clone_and_place(dspec.logo_el, dspec.logo_off, dspec.logo_ext)
    blip = clone.find(".//" + q("a:blip"))
    if blip is None:
        return
    strip_blip_ext_lst(blip)
    rid = f"rIdLogo{id_state['next'] + 1}"
    blip.set("{%s}embed" % R, rid)
    renumber_ids(clone, id_state)
    spTree.append(clone)
    rel_el = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", "../" + logo_media_partname.replace("ppt/", ""))
