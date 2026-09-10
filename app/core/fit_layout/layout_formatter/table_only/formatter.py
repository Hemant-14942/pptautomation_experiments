"""Format a table_only slide — place the input table in TABLE_BOX, same size.

No scaling: row heights and column widths stay exactly as the input had them.
If the table fits in the box it is centered vertically and horizontally.
If it is too big it is anchored to the top-left of the box (may extend past bottom).

PowerPoint XML we edit:

  p:graphicFrame
    p:xfrm
      a:off  x,y   <- we SET position only
      a:ext  cx,cy <- we do NOT change size
    a:graphic / a:tbl / a:tr h=...  <- row heights unchanged
"""

from lxml import etree

from app.core.fit_layout.layout_formatter.title_table_only.table_utils import (
    clone_and_place_table,
    get_table_total_height,
    get_table_width,
)

from .constants import TABLE_BOX


def calculate_table_y(table_height: int, box: dict[str, int]) -> int:
    """Center table vertically in box if it fits; else pin to top of box."""
    if table_height <= box["height"]:
        return box["y"] + (box["height"] - table_height) // 2
    return box["y"]


def calculate_table_x(table_width: int, box: dict[str, int]) -> int:
    """Center table horizontally in box if it fits; else pin to left of box."""
    if table_width <= box["width"]:
        return box["x"] + (box["width"] - table_width) // 2
    return box["x"]


def format_table_only_slide(graphic_frame_el: etree._Element) -> etree._Element:
    """Clone the input table and place it inside TABLE_BOX without resizing.

    Args:
        graphic_frame_el: the table's <p:graphicFrame> XML from the input slide

    Returns:
        cloned table element with updated position only
    """
    table_height = get_table_total_height(graphic_frame_el)
    table_width = get_table_width(graphic_frame_el)
    y = calculate_table_y(table_height, TABLE_BOX)
    x = calculate_table_x(table_width, TABLE_BOX)
    return clone_and_place_table(graphic_frame_el, (x, y))
