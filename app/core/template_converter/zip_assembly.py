"""Assembles the output .pptx zip: reads the template archive, clones each
mapped template slide's background + master/layout relationships, delegates
per-shape emission to shape_emitter.py / table_restyle.py, and rewrites
ppt/presentation.xml, the presentation-level rels, and [Content_Types].xml
to match the new slide count/order.
"""
from __future__ import annotations

import copy
import re
import zipfile
from io import BytesIO
from typing import Any

from lxml import etree

from app.constants.design_tokens_defaults import (
    DEFAULT_MEDIA_CONTENT_TYPE,
    MEDIA_CONTENT_TYPES,
)
from app.constants.presentation_defaults import (
    DEFAULT_NOTES_HEIGHT,
    DEFAULT_NOTES_WIDTH,
    DEFAULT_SLIDE_HEIGHT,
    DEFAULT_SLIDE_WIDTH,
    FIRST_SHAPE_ID_PER_SLIDE,
    FIRST_SLIDE_ID,
)
from app.core.design_spec import DesignSpec
from app.core.style_parser import SlideDesign
from app.core.template_converter.shape_emitter import (
    emit_body,
    emit_heading,
    emit_logo,
    emit_option,
    emit_picture,
    emit_question_icon,
    emit_title_heading,
)
from app.core.template_converter.table_restyle import restyle_table
from app.utils.xml_helpers import q


def scrub_template_slide(slide_xml: etree._Element) -> etree._Element:
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


def clone_template_background(target_sxml: etree._Element, design: SlideDesign) -> None:
    cSld = target_sxml.find(q("p:cSld"))
    if cSld is None:
        return
    existing = cSld.find(q("p:bg"))
    if design.background_xml is None:
        if existing is not None:
            cSld.remove(existing)
        return
    new_bg = etree.fromstring(design.background_xml)
    if existing is not None:
        cSld.replace(existing, new_bg)
    else:
        cSld.insert(0, new_bg)


def read_template_archive(template_path: str) -> tuple[dict[str, bytes], list[etree._Element], list[str]]:
    with open(template_path, "rb") as fh:
        archive_bytes = fh.read()
    zip_f = zipfile.ZipFile(BytesIO(archive_bytes))
    parts: dict[str, bytes] = {n: zip_f.read(n) for n in zip_f.namelist()}
    slide_xmls: list[etree._Element] = []
    layout_rids: list[str] = []
    slide_names = sorted(
        [n for n in parts if re.match(r"ppt/slides/slide\d+\.xml$", n)],
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )
    for sn in slide_names:
        rels_name = sn.replace("slides/", "slides/_rels/") + ".rels"
        rId = ""
        if rels_name in parts:
            rels_root = etree.fromstring(parts[rels_name])
            for rel in rels_root.iter():
                if rel.get("Type", "").endswith("/slideLayout"):
                    rId = rel.get("Id", "")
                    break
        slide_xmls.append(etree.fromstring(parts[sn]))
        layout_rids.append(rId)
    zip_f.close()
    return parts, slide_xmls, layout_rids


def build_output(
    template_parts: dict[str, bytes],
    template_slide_xmls: list[etree._Element],
    template_layout_rids: list[str],
    designs: list[SlideDesign],
    inputs: list[dict[str, Any]],
    plan: dict[int, int],
    dspec: DesignSpec,
) -> dict[str, bytes]:
    """Build the output zip parts (in-memory)."""
    out_parts: dict[str, bytes] = {}

    for name, blob in template_parts.items():
        if (re.match(r"ppt/slides/slide\d+\.xml$", name)
                or re.match(r"ppt/slides/_rels/slide\d+\.xml\.rels$", name)
                or name == "ppt/presentation.xml"
                or re.match(r"ppt/_rels/presentation\.xml\.rels$", name)
                or re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", name)
                or re.match(r"ppt/notesSlides/_rels/notesSlide\d+\.xml\.rels$", name)):
            continue
        out_parts[name] = blob

    # If the design spec carries a cloneable logo, make sure its image
    # bytes exist in the output under a stable, dedicated media partname
    # (the slide it was originally cloned from may not be one we reuse).
    logo_media_partname: str | None = None
    if dspec.logo_el is not None and dspec.logo_image_bytes is not None:
        ext = dspec.logo_image_ext or "png"
        logo_media_partname = f"ppt/media/design_spec_logo.{ext}"
        out_parts[logo_media_partname] = dspec.logo_image_bytes

    # Same idea for the title-banner's corner icon.
    title_icon_media_partname: str | None = None
    if dspec.title_icon_el is not None and dspec.title_icon_image_bytes is not None:
        ext = dspec.title_icon_image_ext or "png"
        title_icon_media_partname = f"ppt/media/design_spec_title_icon.{ext}"
        out_parts[title_icon_media_partname] = dspec.title_icon_image_bytes

    question_icon_media_partname: str | None = None
    if dspec.question_icon_el is not None and dspec.question_icon_image_bytes is not None:
        ext = dspec.question_icon_image_ext or "png"
        question_icon_media_partname = f"ppt/media/design_spec_question_icon.{ext}"
        out_parts[question_icon_media_partname] = dspec.question_icon_image_bytes

    # Unique, deck-wide counter for media partnames of content pictures
    # carried over (as-is) from the input deck.
    pic_media_state = {"next": 0}

    n = len(inputs)
    next_slide_id = FIRST_SLIDE_ID
    pres_rels_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"

    # ppt/presentation.xml is reused close to verbatim from the template
    # (see build_presentation_xml) -- including its own r:id references
    # to the slide master, notes master, embedded fonts, theme, table
    # styles, etc. Those relationships have to survive into the output's
    # presentation.xml.rels too, or the presentation has no resolvable
    # master/theme at all. Start from the template's own rels and only
    # drop+rebuild the "slide" entries (we don't reuse the template's
    # own slide count/order); everything else carries over untouched.
    tmpl_pres_rels_blob = template_parts.get("ppt/_rels/presentation.xml.rels")
    if tmpl_pres_rels_blob:
        new_pres_rels = etree.fromstring(tmpl_pres_rels_blob)
        for rel in list(new_pres_rels):
            if rel.get("Type", "").endswith("/slide"):
                new_pres_rels.remove(rel)
    else:
        new_pres_rels = etree.Element(pres_rels_ns + "Relationships")

    template_layout_partnames: list[str] = []
    for slide_name in sorted(
        [n_ for n_ in template_parts if re.match(r"ppt/slides/slide\d+\.xml$", n_)],
        key=lambda n_: int(re.search(r"slide(\d+)", n_).group(1)),
    ):
        rels_name = slide_name.replace("slides/", "slides/_rels/") + ".rels"
        target_layout = ""
        if rels_name in template_parts:
            for rel in etree.fromstring(template_parts[rels_name]).iter():
                if rel.get("Type", "").endswith("/slideLayout"):
                    target_layout = rel.get("Target", "").lstrip("/")
                    break
        template_layout_partnames.append(target_layout or "ppt/slideLayouts/slideLayout1.xml")

    used_layouts: dict[str, str] = {}
    for i, info in enumerate(inputs):
        design_idx = plan.get(info["index"], 0) % len(designs)
        design = designs[design_idx]
        tmpl_slide_xml = template_slide_xmls[design_idx]
        tmpl_layout_partname = template_layout_partnames[design_idx]
        tmpl_slide_name = sorted(
            [n_ for n_ in template_parts if re.match(r"ppt/slides/slide\d+\.xml$", n_)],
            key=lambda n_: int(re.search(r"slide(\d+)", n_).group(1)),
        )[design_idx]
        tmpl_rels_name = tmpl_slide_name.replace("slides/", "slides/_rels/") + ".rels"

        fresh = scrub_template_slide(tmpl_slide_xml)
        clone_template_background(fresh, design)
        spTree = fresh.find(q("p:cSld") + "/" + q("p:spTree"))

        slide_rels_xml = etree.Element(pres_rels_ns + "Relationships")

        id_state = {"next": FIRST_SHAPE_ID_PER_SLIDE}
        for item in info["items"]:
            kind = item["kind"]
            if kind == "heading":
                emit_heading(spTree, item, dspec, id_state)
            elif kind == "title_heading":
                emit_title_heading(spTree, item, dspec, id_state, slide_rels_xml, pres_rels_ns, title_icon_media_partname)
            elif kind == "option":
                emit_option(spTree, item, dspec, id_state)
            elif kind == "table":
                tbl_el = copy.deepcopy(item["xml"])
                restyle_table(tbl_el, dspec)
                spTree.append(tbl_el)
            elif kind == "picture":
                emit_picture(spTree, item, dspec, id_state, slide_rels_xml, pres_rels_ns, out_parts, pic_media_state)
            else:
                emit_body(spTree, item, dspec)

        if any(it.get("kind") == "heading" for it in info["items"]):
            emit_question_icon(
                spTree, dspec, id_state, slide_rels_xml, pres_rels_ns, question_icon_media_partname,
            )

        emit_logo(spTree, dspec, id_state, slide_rels_xml, pres_rels_ns, logo_media_partname)

        slide_partname = f"ppt/slides/slide{i+1}.xml"
        out_parts[slide_partname] = etree.tostring(
            fresh, xml_declaration=True, encoding="UTF-8", standalone=True
        )

        layout_rid = used_layouts.get(tmpl_layout_partname)
        if layout_rid is None:
            layout_rid = f"rIdLayout{len(used_layouts)+1}"
            used_layouts[tmpl_layout_partname] = layout_rid
            rel_el = etree.SubElement(new_pres_rels, pres_rels_ns + "Relationship")
            rel_el.set("Id", layout_rid)
            rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout")
            rel_el.set("Target", tmpl_layout_partname.replace("ppt/", ""))

        slide_rid = f"rId{i+100}"
        rel_el = etree.SubElement(new_pres_rels, pres_rels_ns + "Relationship")
        rel_el.set("Id", slide_rid)
        rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide")
        rel_el.set("Target", f"slides/slide{i+1}.xml")

        rel_el2 = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
        rel_el2.set("Id", layout_rid)
        rel_el2.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout")
        rel_el2.set("Target", tmpl_layout_partname.replace("ppt/", ""))

        # Carry over image / notes relationships from the template slide so
        # the background <p:bg><a:blip r:embed="rId3"> resolves to an
        # actual image part in the output zip.
        if tmpl_rels_name in template_parts:
            tmpl_rels_root = etree.fromstring(template_parts[tmpl_rels_name])
            for rel in tmpl_rels_root:
                rtype = rel.get("Type", "")
                if rtype.endswith("/image"):
                    image_rel = etree.SubElement(slide_rels_xml, pres_rels_ns + "Relationship")
                    image_rel.set("Id", rel.get("Id"))
                    image_rel.set("Type", rtype)
                    image_rel.set("Target", rel.get("Target"))

        out_parts[f"ppt/slides/_rels/slide{i+1}.xml.rels"] = etree.tostring(
            slide_rels_xml, xml_declaration=True, encoding="UTF-8", standalone=True
        )

    pres_xml = build_presentation_xml(
        n,
        start_id=next_slide_id,
        slide_width=_extract_int_attr(template_parts.get("ppt/presentation.xml", b""), "p:sldSz", "cx", DEFAULT_SLIDE_WIDTH),
        slide_height=_extract_int_attr(template_parts.get("ppt/presentation.xml", b""), "p:sldSz", "cy", DEFAULT_SLIDE_HEIGHT),
        notes_size=_extract_notes_size(template_parts.get("ppt/presentation.xml", b"")),
        default_text_style=_extract_default_text_style(template_parts.get("ppt/presentation.xml", b"")),
        base_pres_xml=template_parts.get("ppt/presentation.xml"),
    )
    out_parts["ppt/presentation.xml"] = etree.tostring(
        pres_xml, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    out_parts["ppt/_rels/presentation.xml.rels"] = etree.tostring(
        new_pres_rels, xml_declaration=True, encoding="UTF-8", standalone=True
    )

    if "[Content_Types].xml" in out_parts:
        out_parts["[Content_Types].xml"] = update_content_types(out_parts["[Content_Types].xml"], n, out_parts)

    return out_parts


def build_presentation_xml(
    num_slides: int,
    start_id: int = FIRST_SLIDE_ID,
    slide_width: int = DEFAULT_SLIDE_WIDTH,
    slide_height: int = DEFAULT_SLIDE_HEIGHT,
    notes_size: tuple[int, int] | None = None,
    default_text_style: etree._Element | None = None,
    base_pres_xml: bytes | None = None,
) -> etree._Element:
    """Reuse the template's presentation.xml as the wrapper so the lxml
    element types match what python-pptx expects, then rewrite the
    sldIdLst with our new slide ids/rIds."""
    if base_pres_xml:
        pres_xml = etree.fromstring(base_pres_xml)
    else:
        pres_xml = etree.fromstring(
            b"""<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                   xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                   xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <p:sldMasterIdLst>
        <p:sldMasterId id="2147483648" r:id="rId1"/>
      </p:sldMasterIdLst>
      <p:sldIdLst>
      </p:sldIdLst>
    </p:presentation>"""
        )

    sldIdLst = pres_xml.find(q("p:sldIdLst"))
    if sldIdLst is None:
        sldIdLst = etree.SubElement(pres_xml, q("p:sldIdLst"))
    for child in list(sldIdLst):
        sldIdLst.remove(child)
    for i in range(num_slides):
        sldId = etree.SubElement(sldIdLst, q("p:sldId"))
        sldId.set("id", str(start_id + i))
        sldId.set(q("r:id"), f"rId{i+100}")

    sldSz = pres_xml.find(q("p:sldSz"))
    if sldSz is None:
        sldSz = etree.SubElement(pres_xml, q("p:sldSz"))
    sldSz.set("cx", str(slide_width))
    sldSz.set("cy", str(slide_height))

    notesSz = pres_xml.find(q("p:notesSz"))
    if notesSz is None:
        notesSz = etree.SubElement(pres_xml, q("p:notesSz"))
    notesSz.set("cx", str(notes_size[0]) if notes_size else str(DEFAULT_NOTES_WIDTH))
    notesSz.set("cy", str(notes_size[1]) if notes_size else str(DEFAULT_NOTES_HEIGHT))
    return pres_xml


def _extract_int_attr(xml_blob: bytes, tag: str, attr: str, default: int) -> int:
    if not xml_blob:
        return default
    root = etree.fromstring(xml_blob)
    el = root.find(q(tag))
    if el is None:
        return default
    try:
        return int(el.get(attr, default))
    except (ValueError, TypeError):
        return default


def _extract_notes_size(xml_blob: bytes) -> tuple[int, int] | None:
    if not xml_blob:
        return None
    root = etree.fromstring(xml_blob)
    el = root.find(q("p:notesSz"))
    if el is None:
        return None
    try:
        return (int(el.get("cx", DEFAULT_NOTES_WIDTH)), int(el.get("cy", DEFAULT_NOTES_HEIGHT)))
    except (ValueError, TypeError):
        return None


def _extract_default_text_style(xml_blob: bytes) -> etree._Element | None:
    if not xml_blob:
        return None
    root = etree.fromstring(xml_blob)
    el = root.find(q("p:defaultTextStyle"))
    return copy.deepcopy(el) if el is not None else None


def update_content_types(content_types_blob: bytes, num_slides: int, out_parts: dict[str, bytes]) -> bytes:
    """Ensure each slideN.xml has an Override in [Content_Types].xml, and
    that every media extension actually present under ppt/media/ in the
    output (logo, title icon, carried-over input pictures, ...) has a
    Default entry if it's a type not already present in the template's
    own content types."""
    CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    root = etree.fromstring(content_types_blob)
    existing = {
        ov.get("PartName"): ov
        for ov in root.findall(CT + "Override")
        if ov.get("PartName", "").startswith("/ppt/slides/slide")
    }
    for i in range(1, num_slides + 1):
        part = f"/ppt/slides/slide{i}.xml"
        if part in existing:
            continue
        ov = etree.SubElement(root, CT + "Override")
        ov.set("PartName", part)
        ov.set(
            "ContentType",
            "application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
        )

    media_exts = {
        name.rsplit(".", 1)[-1].lower()
        for name in out_parts
        if name.startswith("ppt/media/") and "." in name
    }
    existing_exts = {d.get("Extension", "").lower() for d in root.findall(CT + "Default")}
    for ext in sorted(media_exts - existing_exts):
        default = etree.SubElement(root, CT + "Default")
        default.set("Extension", ext)
        default.set("ContentType", MEDIA_CONTENT_TYPES.get(ext, DEFAULT_MEDIA_CONTENT_TYPE))

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
