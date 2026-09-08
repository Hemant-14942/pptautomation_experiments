from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class TemplateArchive:
    parts: dict[str, bytes]
    slide_count: int
    output_shell_xml: etree._Element
    output_shell_partname: str
