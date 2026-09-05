from lxml import etree

from .constants import TABLE_BOX
from .table_utils import clone_and_place_table, get_table_total_height, get_table_width


def calculate_table_y(table_height: int, box: dict[str, int]) -> int:
    """Center vertically if the table fits in the box; otherwise anchor
    to the top of the box instead of overflowing further down."""
    if table_height <= box["height"]:
        return box["y"] + (box["height"] - table_height) // 2
    return box["y"]


def calculate_table_x(table_width: int, box: dict[str, int]) -> int:
    """Center horizontally if the table fits in the box; otherwise anchor
    to the left edge of the box instead of overflowing further right."""
    if table_width <= box["width"]:
        return box["x"] + (box["width"] - table_width) // 2
    return box["x"]


def format_table_only(graphic_frame_el: etree._Element) -> etree._Element:
    """Clone the input slide's table, centered in the box on both axes
    (or anchored to top/left if it's bigger than the box on that axis).
    Width/height are left exactly as the input had them."""
    table_height = get_table_total_height(graphic_frame_el)
    table_width = get_table_width(graphic_frame_el)
    y = calculate_table_y(table_height, TABLE_BOX)
    x = calculate_table_x(table_width, TABLE_BOX)
    return clone_and_place_table(graphic_frame_el, (x, y))
