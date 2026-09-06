"""
=============================================================================
FUNCTION OVERVIEW: read_template_archive(template_path: str) -> TemplateArchive
=============================================================================

1. WHAT IT DOES:
   Loads a PowerPoint (.pptx) template completely into RAM without touching disk 
   after the initial read. It separates raw assets (images/themes) from slide XML 
   trees so they can be inspected, duplicated, or modified programmatically.

2. PPTX INTERNAL ARCHIVE STRUCTURE:
   A .pptx file is a ZIP archive adhering to the ECMA-376 (OOXML) specification:
   
   template.pptx (ZIP Archive)
   ├── [Content_Types].xml               <- MIME types of all parts
   ├── _rels/.rels                       <- Root package relationships
   └── ppt/
       ├── presentation.xml              <- Deck ordering & global settings
       ├── presentation.xml.rels         <- Links presentation to slides/layouts
       ├── slides/
       │   ├── slide1.xml                <- Individual slide shapes/text (parsed into slide_xmls)
       │   └── _rels/
       │       └── slide1.xml.rels       <- Resolves slide dependencies (parsed for layout rId)
       ├── slideLayouts/
       │   └── slideLayout1.xml          <- Placeholder structures/floorplans
       ├── slideMasters/
       │   └── slideMaster1.xml          <- Global master theme, logo, fonts
       └── media/                        <- Embedded binaries (image1.png, font.ttf)

3. STEP-BY-STEP EXECUTION FLOW:
   a. In-Memory Extraction:
      - Reads the full file as raw bytes via BytesIO.
      - Extracts every entry into a `parts: dict[str, bytes]` map (path -> binary).
      - Closes the ZIP handle immediately to prevent memory/handle leaks.

   b. Slide Discovery & Numeric Sorting:
      - Uses regex `ppt/slides/slide\d+\.xml$` to match only slide content XMLs.
      - Uses a custom lambda sort key `int(re.search(r"slide(\d+)", ...))` to 
        enforce numeric slide order (e.g., slide2.xml comes before slide10.xml).

   c. Relationship & Layout Mapping:
      - Derives companion relationship file paths: 
        `ppt/slides/slide1.xml` -> `ppt/slides/_rels/slide1.xml.rels`.
      - Parses the .rels XML to locate the `<Relationship>` of type `/slideLayout`.
      - Extracts its `Id` (e.g., "rId1") into `layout_rids`. This ID is vital 
        because PowerPoint corrupts if a rebuilt slide lacks its layout link.

   d. XML Tree Parsing:
      - Parses raw bytes of each slide into an active `lxml.etree._Element` tree.
      - Aligns slide index with layout index (`slide_xmls[i]` maps to `layout_rids[i]`).

4. RETURNS:
   A `TemplateArchive` domain model containing:
   - `parts`: Unmodified binary assets & non-slide XMLs for final package rebuild.
   - `slide_xmls`: Ordered, mutable lxml element trees representing slide content.
   - `layout_rids`: Ordered list of relationship IDs linking each slide to its layout.
=============================================================================
"""

from __future__ import annotations

import re
import zipfile
from io import BytesIO

from lxml import etree

from app.dynamic_rendering.domain.models.template_archive import TemplateArchive


def read_template_archive(template_path: str) -> TemplateArchive:
    # open the .pptx file on disk in binary mode
    with open(template_path, "rb") as fh:
        # read entire file into memory as bytes
        archive_bytes = fh.read()

    # treat those bytes as a ZIP archive (pptx is a zip)
    zip_f = zipfile.ZipFile(BytesIO(archive_bytes))

    # build dict: every path inside zip → file contents as bytes
    parts: dict[str, bytes] = {n: zip_f.read(n) for n in zip_f.namelist()}

    # we will fill these two lists one entry per slide
    slide_xmls: list[etree._Element] = []
    layout_rids: list[str] = []

    # find all slide xml paths like ppt/slides/slide1.xml, slide2.xml, ...
    slide_names = sorted(
        [n for n in parts if re.match(r"ppt/slides/slide\d+\.xml$", n)],
        # sort by slide number so slide1 comes before slide2
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )

    # process each slide one by one
    for sn in slide_names:
        # build rels path: ppt/slides/slide1.xml → ppt/slides/_rels/slide1.xml.rels
        rels_name = sn.replace("slides/", "slides/_rels/") + ".rels"

        # default layout id if rels file missing
        r_id = ""

        # if this slide has a .rels file, read which layout it uses
        if rels_name in parts:
            # parse rels xml from bytes
            rels_root = etree.fromstring(parts[rels_name])
            # walk every relationship entry
            for rel in rels_root.iter():
                # look for link type ending in /slideLayout
                if rel.get("Type", "").endswith("/slideLayout"):
                    # save Id like "rId1" — used when we rebuild output rels
                    r_id = rel.get("Id", "")
                    break

        # parse slide xml bytes into lxml tree and append to list
        slide_xmls.append(etree.fromstring(parts[sn]))
        # keep layout rId aligned with same slide index
        layout_rids.append(r_id)

    # close zip handle
    zip_f.close()

    # wrap everything in our domain object and return
    return TemplateArchive(parts=parts, slide_xmls=slide_xmls, layout_rids=layout_rids)