from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class TemplateArchive:
    # Every file inside the .pptx zip: path → raw bytes
    # Example keys: "ppt/slides/slide1.xml", "ppt/media/image1.png"
    parts: dict[str, bytes]

    # Parsed XML tree for each slide, in order: slide1, slide2, ...
    # Same order as ppt/slides/slide1.xml, slide2.xml, ...
    slide_xmls: list[etree._Element]

    # For each slide, the relationship id that points to its slideLayout
    # Read from ppt/slides/_rels/slideN.xml.rels
    # Example: "rId1" → links to ppt/slideLayouts/slideLayout5.xml
    layout_rids: list[str]