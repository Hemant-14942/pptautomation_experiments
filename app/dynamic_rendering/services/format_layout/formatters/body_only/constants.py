"""Fixed textbox size for the body_only slide type.

A body_only slide has NO heading/title — just one big text box that fills
the slide (with small margins on all four sides).

Canvas: 40 inches wide × 22.5 inches tall.
PowerPoint stores sizes in EMU (English Metric Units).
1 inch = 914,400 EMU.
"""

# ---------------------------------------------------------------------------
# Slide size (same for every slide in this project)
# ---------------------------------------------------------------------------
INCH_EMU = 914_400          # 1 inch in EMU units
SLIDE_WIDTH_EMU = 40 * INCH_EMU    # 36,576,000  → 40 inches wide
SLIDE_HEIGHT_EMU = 22.5 * INCH_EMU  # 20,574,000  → 22.5 inches tall

# Empty space we leave on every side of the slide (like a page margin).
SIDE_MARGIN_EMU = INCH_EMU  # 1 inch margin on left, right, top, and bottom

# ---------------------------------------------------------------------------
# The one text box that holds ALL body content on a body_only slide
# ---------------------------------------------------------------------------
# Position: 1 inch from the left edge, 1 inch from the top edge.
# Size:     38 inches wide  (40 - 1 left margin - 1 right margin)
#           20.5 inches tall (22.5 - 1 top margin - 1 bottom margin)
#
# Text inside this box will be:
#   - left-aligned horizontally
#   - centered vertically (equal gap above and below the text block)
#   - wrapped to multiple lines when needed
#   - shrunk by PowerPoint if the text is too long (normAutofit)
BODY_TEXTBOX = {
    "x": SIDE_MARGIN_EMU,                              # 1" from left
    "y": SIDE_MARGIN_EMU,                              # 1" from top
    "width": SLIDE_WIDTH_EMU - 2 * SIDE_MARGIN_EMU,    # 38" wide
    "height": SLIDE_HEIGHT_EMU - 2 * SIDE_MARGIN_EMU, # 20.5" tall
}
