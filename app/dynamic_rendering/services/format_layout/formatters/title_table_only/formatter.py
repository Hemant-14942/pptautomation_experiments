"""Place the input table inside TABLE_BOX, scaling rows/fonts when needed."""

from lxml import etree

from app.dynamic_rendering.services.format_layout.formatters.title_table_only.constants import table_box_for
from app.dynamic_rendering.services.format_layout.shared.table_utils import format_table_in_box


def format_table(graphic_frame_el: etree._Element, dspec=None) -> etree._Element:
    return format_table_in_box(graphic_frame_el, table_box_for(dspec))
