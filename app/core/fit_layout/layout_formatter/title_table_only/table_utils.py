"""
The table's XML tree (from what we found earlier):


<p:graphicFrame>                          <- graphic_frame_el (the whole table shape)
  <p:nvGraphicFramePr>...</p:nvGraphicFramePr>     (child index 0)
  <p:xfrm>                                          (child index 1, if present)
    <a:off x="..." y="..."/>
    <a:ext cx="..." cy="..."/>
  </p:xfrm>
  <a:graphic>
    <a:graphicData uri="...table">
      <a:tbl>                             <- nested several levels deep
        <a:tblGrid>...</a:tblGrid>
        <a:tr h="...">...</a:tr>          <- row 1
        <a:tr h="...">...</a:tr>          <- row 2
      </a:tbl>
    </a:graphicData>
  </a:graphic>
</p:graphicFrame>
"""

import copy

from lxml import etree

from app.utils.xml_helpers import q


def get_table_total_height(graphic_frame_el: etree._Element) -> int:
    """Sum of all <a:tr h="..."> values (EMU) -- the table's real height,
    independent of whatever <p:xfrm><a:ext cy> currently says."""
    tbl = graphic_frame_el.find(".//" + q("a:tbl"))
    return sum(int(tr.get("h")) for tr in tbl.findall(q("a:tr")))


def get_table_width(graphic_frame_el: etree._Element) -> int:
    """The table's own width (EMU) from its existing <p:xfrm><a:ext cx>.
    Used for horizontal centering -- never modified."""
    xfrm = graphic_frame_el.find(q("p:xfrm"))
    ext = xfrm.find(q("a:ext")) if xfrm is not None else None
    return int(ext.get("cx")) if ext is not None else 0


def clone_and_place_table(
    graphic_frame_el: etree._Element, off: tuple[int, int]
) -> etree._Element:
    """Deep-copy a graphicFrame and set its <p:xfrm><a:off> only.

    Only position (x, y) is changed -- width/height (a:ext) are left
    exactly as the input had them, since resizing a table means rescaling
    every row height / column width, which we deliberately do not do.
    """
    clone = copy.deepcopy(graphic_frame_el)
    #  p:xfrm = "transform" — it's the tag PowerPoint uses to record an element's position and size on the slide. It holds two children:
    # <a:off x="..." y="..."> — where the top-left corner sits (offset from the slide's origin)
    # <a:ext cx="..." cy="..."> — how big it is (width/height)

    xfrm = clone.find(q("p:xfrm"))
    if xfrm is None:
        xfrm = etree.Element(q("p:xfrm"))
        clone.insert(1, xfrm)  # after nvGraphicFramePr, before a:graphic
    off_el = xfrm.find(q("a:off"))
    if off_el is None:
        off_el = etree.SubElement(xfrm, q("a:off"))
    off_el.set("x", str(off[0]))
    off_el.set("y", str(off[1]))
    return clone
