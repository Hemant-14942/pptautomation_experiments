"""Place the input table inside TABLE_BOX without resizing."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.table_only.constants import TABLE_BOX
from app.dynamic_rendering.services.format_layout.shared.table_utils import (
    clone_and_place_table,
    get_table_total_height,
    get_table_width,
)


def _calculate_table_y(table_height: int, box: dict[str, int]) -> int:
    if table_height <= box["height"]:
        return box["y"] + (box["height"] - table_height) // 2
    return box["y"]


def _calculate_table_x(table_width: int, box: dict[str, int]) -> int:
    if table_width <= box["width"]:
        return box["x"] + (box["width"] - table_width) // 2
    return box["x"]


def format_table(graphic_frame_el: etree._Element) -> etree._Element:
    table_height = get_table_total_height(graphic_frame_el)
    table_width = get_table_width(graphic_frame_el)
    y = _calculate_table_y(table_height, TABLE_BOX)
    x = _calculate_table_x(table_width, TABLE_BOX)
    return clone_and_place_table(graphic_frame_el, (x, y))
