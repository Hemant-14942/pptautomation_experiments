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


def get_table_total_width(graphic_frame_el: etree._Element) -> int:
    """Sum of all <a:gridCol w="..."> values (EMU) -- the table's real width,
    independent of whatever <p:xfrm><a:ext cx> currently says."""
    grid = graphic_frame_el.find(".//" + q("a:tblGrid"))
    return sum(int(col.get("w")) for col in grid.findall(q("a:gridCol")))


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


def _set_table_frame_ext(graphic_frame_el: etree._Element, width: int, height: int) -> None:
    """Write the graphicFrame's <p:xfrm><a:ext> so it always matches the table's
    real tblGrid/row size -- keeps the declared box and the real content in sync."""
    xfrm = graphic_frame_el.find(q("p:xfrm"))
    if xfrm is None:
        xfrm = etree.Element(q("p:xfrm"))
        graphic_frame_el.insert(1, xfrm)
    ext = xfrm.find(q("a:ext"))
    if ext is None:
        ext = etree.SubElement(xfrm, q("a:ext"))
    ext.set("cx", str(width))
    ext.set("cy", str(height))


def _scale_row_heights(graphic_frame_el: etree._Element, scale: float) -> None:
    tbl = graphic_frame_el.find(".//" + q("a:tbl"))
    if tbl is None:
        return
    for tr in tbl.findall(q("a:tr")):
        h_attr = tr.get("h")
        if not h_attr:
            continue
        tr.set("h", str(max(1, int(int(h_attr) * scale))))


def _scale_col_widths(graphic_frame_el: etree._Element, scale: float) -> None:
    grid = graphic_frame_el.find(".//" + q("a:tblGrid"))
    if grid is None:
        return
    for col in grid.findall(q("a:gridCol")):
        w_attr = col.get("w")
        if not w_attr:
            continue
        col.set("w", str(max(1, int(int(w_attr) * scale))))


def fit_table_to_box(graphic_frame_el: etree._Element, max_width: int, max_height: int) -> float | None:
    """Shrink rows, columns and cell fonts when the table's real size (from
    tblGrid/rows, never the possibly-stale xfrm) is bigger than the box.

    Mutates graphic_frame_el in place. Returns the scale factor applied, or None
    when no scaling was needed.
    """
    table_width = get_table_total_width(graphic_frame_el)
    table_height = get_table_total_height(graphic_frame_el)
    if table_width <= 0 or table_height <= 0:
        return None

    width_scale = min(1.0, max_width / table_width)
    height_scale = min(1.0, max_height / table_height)
    scale = min(width_scale, height_scale)
    if scale >= 1.0:
        return None

    _scale_row_heights(graphic_frame_el, scale)
    _scale_col_widths(graphic_frame_el, scale)
    _scale_table_fonts(graphic_frame_el, scale)
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
    """Clone a table, scale to fit the box if needed, then center in box.

    Width and height are always read from the table's real tblGrid/rows (never
    the graphicFrame's own xfrm, which can be stale/wrong on some input decks),
    and the xfrm is rewritten to match before placement -- so the declared box
    and the real content never disagree again.
    """
    clone = copy.deepcopy(graphic_frame_el)
    fit_table_to_box(clone, box["width"], box["height"])
    table_width = get_table_total_width(clone)
    table_height = get_table_total_height(clone)
    _set_table_frame_ext(clone, table_width, table_height)
    x = _anchor_in_box(table_width, box["x"], box["width"])
    y = _anchor_in_box(table_height, box["y"], box["height"])
    return place_table(clone, (x, y))


def clone_and_place_table(
    graphic_frame_el: etree._Element, off: tuple[int, int]
) -> etree._Element:
    """Deep-copy a graphicFrame and set its <p:xfrm><a:off> only."""
    clone = copy.deepcopy(graphic_frame_el)
    return place_table(clone, off)
