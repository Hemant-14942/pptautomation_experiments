"""Fixed table placement box for the table_only slide type.

A table_only slide has NO heading, NO body text, NO images, NO question pill —
just one table.

Canvas: 40 inches wide x 22.5 inches tall.
1 inch = 914,400 EMU.

Layout (same vertical band as title_table_only, but with 1in bottom margin):
  - Top:    5.151in from slide top (where the heading pill ends on other slides)
  - Bottom: 1in margin from slide bottom
  - Width:  32in (80% of 40in slide width)
  - Left:   1in from slide left edge
"""

INCH_EMU = 914_400
SLIDE_WIDTH_EMU = 40 * INCH_EMU
SLIDE_HEIGHT_EMU = 22.5 * INCH_EMU

# Where the heading pill ends on title-based slides (start table box here).
BOX_TOP_EMU = 4_711_025  # 5.151 inches

# Empty space at the bottom of the slide.
BOTTOM_MARGIN_EMU = INCH_EMU  # 1 inch

# Table box: 80% slide width, from below-heading down to 1in bottom margin.
TABLE_BOX = {
    "x": INCH_EMU,                              # 1in from left
    "y": BOX_TOP_EMU,                           # 5.151in from top
    "width": int(SLIDE_WIDTH_EMU * 0.80),       # 32in (80% of 40in)
    "height": SLIDE_HEIGHT_EMU - BOX_TOP_EMU - BOTTOM_MARGIN_EMU,  # ~16.35in
}
