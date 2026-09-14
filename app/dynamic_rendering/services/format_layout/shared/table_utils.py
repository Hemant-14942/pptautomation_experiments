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

from app.dynamic_rendering.utils.xml.helpers import q

_MIN_FONT_SZ = 1000  # 8pt in OOXML 1/100-pt units


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


def _scale_rpr_sz(rPr: etree._Element, scale: float) -> None:
    sz = rPr.get("sz")
    if not sz:
        return
    new_sz = max(_MIN_FONT_SZ, int(int(sz) * scale))
    rPr.set("sz", str(new_sz))


def _scale_table_fonts(graphic_frame_el: etree._Element, scale: float) -> None:
    tbl = graphic_frame_el.find(".//" + q("a:tbl"))
    if tbl is None:
        return
    for tag in ("a:rPr", "a:endParaRPr", "a:defRPr"):
        for rPr in tbl.iter(q(tag)):
            _scale_rpr_sz(rPr, scale)


def _set_table_frame_height(graphic_frame_el: etree._Element, height: int) -> None:
    xfrm = graphic_frame_el.find(q("p:xfrm"))
    if xfrm is None:
        return
    ext = xfrm.find(q("a:ext"))
    if ext is not None:
        ext.set("cy", str(height))


def fit_table_to_box(graphic_frame_el: etree._Element, max_height: int) -> float | None:
    """Shrink row heights and cell fonts when the table is taller than max_height.

    Mutates graphic_frame_el in place. Returns the scale factor applied, or None
    when no scaling was needed.
    """
    table_height = get_table_total_height(graphic_frame_el)
    if table_height <= max_height or table_height <= 0:
        return None

    scale = max_height / table_height
    tbl = graphic_frame_el.find(".//" + q("a:tbl"))
    if tbl is None:
        return None

    for tr in tbl.findall(q("a:tr")):
        h_attr = tr.get("h")
        if not h_attr:
            continue
        tr.set("h", str(max(1, int(int(h_attr) * scale))))

    _scale_table_fonts(graphic_frame_el, scale)
    _set_table_frame_height(graphic_frame_el, get_table_total_height(graphic_frame_el))
    return scale


def _anchor_in_box(content_size: int, box_start: int, box_size: int) -> int:
    if content_size <= box_size:
        return box_start + (box_size - content_size) // 2
    return box_start


def place_table(graphic_frame_el: etree._Element, off: tuple[int, int]) -> etree._Element:
    """Set top-left position on a table graphicFrame (mutates in place)."""
    xfrm = graphic_frame_el.find(q("p:xfrm"))
    if xfrm is None:
        xfrm = etree.Element(q("p:xfrm"))
        graphic_frame_el.insert(1, xfrm)
    off_el = xfrm.find(q("a:off"))
    if off_el is None:
        off_el = etree.SubElement(xfrm, q("a:off"))
    off_el.set("x", str(off[0]))
    off_el.set("y", str(off[1]))
    return graphic_frame_el


def format_table_in_box(graphic_frame_el: etree._Element, box: dict[str, int]) -> etree._Element:
    """Clone a table, scale to fit box height if needed, then center or top-anchor in box."""
    clone = copy.deepcopy(graphic_frame_el)
    fit_table_to_box(clone, box["height"])
    table_height = get_table_total_height(clone)
    table_width = get_table_width(clone)
    x = _anchor_in_box(table_width, box["x"], box["width"])
    y = _anchor_in_box(table_height, box["y"], box["height"])
    return place_table(clone, (x, y))


def clone_and_place_table(
    graphic_frame_el: etree._Element, off: tuple[int, int]
) -> etree._Element:
    """Deep-copy a graphicFrame and set its <p:xfrm><a:off> only."""
    clone = copy.deepcopy(graphic_frame_el)
    return place_table(clone, off)
