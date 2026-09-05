"""Fixed content-area box for the title_table_only slide type.

Below the heading pill, spanning most of the slide width, down to the
ACTUAL slide bottom. The table's own size (row heights, column widths) is
never changed -- this box is only used to decide WHERE to place the table
(see formatter.py's center-or-top logic), never to resize it.

Canvas: 36,576,000 x 20,574,000 EMU (40 x 22.5 inches). 1 inch = 914,400 EMU.
"""

SLIDE_HEIGHT_EMU = 20_574_000  # 22.5 inches

# Table content area (below heading pill, most of the slide width).
# Position: 1.0in from left, 5.151in from top.
# Width: 32in (80% of 40in slide width).
# Height: computed as slide_height - y, so the box's bottom edge lands
# exactly on the real slide bottom (17.348in) -- NOT the 19.015in value
# title_body_only originally used, which was copied from a real textbox
# in test3.pptx that itself overflows 1.674in past the visible slide edge
# (harmless for a wrapping text box, but wrong for centering math).
_BOX_Y = 4711025
TABLE_BOX = {
    "x": 914400,
    "y": _BOX_Y,
    "width": 29260560,
    "height": SLIDE_HEIGHT_EMU - _BOX_Y,
}
