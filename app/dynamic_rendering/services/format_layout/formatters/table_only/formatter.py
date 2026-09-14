"""Place the input table inside TABLE_BOX, scaling rows/fonts when needed."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.table_only.constants import TABLE_BOX
from app.dynamic_rendering.services.format_layout.shared.table_utils import format_table_in_box


def format_table(graphic_frame_el: etree._Element) -> etree._Element:
    return format_table_in_box(graphic_frame_el, TABLE_BOX)
