"""Update [Content_Types].xml for new slides and media parts."""

from __future__ import annotations

from lxml import etree

from app.dynamic_rendering.constants.design_tokens_defaults import (
    DEFAULT_MEDIA_CONTENT_TYPE,
    MEDIA_CONTENT_TYPES,
)


def update_content_types(content_types_blob: bytes, num_slides: int, out_parts: dict[str, bytes]) -> bytes:
    """Add slide overrides and media Default entries missing from the template."""
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
