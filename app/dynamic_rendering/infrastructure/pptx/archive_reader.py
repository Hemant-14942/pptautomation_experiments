"""
Read a template .pptx from disk into a TemplateArchive object.

Loads the full ZIP plus only the output shell slide XML (default: last slide).
"""

from __future__ import annotations

import re
import zipfile
from io import BytesIO

from lxml import etree

from app.dynamic_rendering.constants.template_design import OUTPUT_TEMPLATE_SLIDE_INDEX, resolve_slide_index
from app.dynamic_rendering.domain.models.template_archive import TemplateArchive


def read_template_archive(template_path: str) -> TemplateArchive:
    with open(template_path, "rb") as fh:
        archive_bytes = fh.read()

    zip_f = zipfile.ZipFile(BytesIO(archive_bytes))
    parts: dict[str, bytes] = {n: zip_f.read(n) for n in zip_f.namelist()}

    slide_names = sorted(
        [n for n in parts if re.match(r"ppt/slides/slide\d+\.xml$", n)],
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )
    slide_count = len(slide_names)
    shell_index = resolve_slide_index(OUTPUT_TEMPLATE_SLIDE_INDEX, slide_count)
    output_shell_partname = slide_names[shell_index] if slide_names else "ppt/slides/slide1.xml"
    output_shell_xml = etree.fromstring(parts[output_shell_partname]) if slide_names else etree.Element("sld")

    zip_f.close()
    return TemplateArchive(
        parts=parts,
        slide_count=slide_count,
        output_shell_xml=output_shell_xml,
        output_shell_partname=output_shell_partname,
    )
