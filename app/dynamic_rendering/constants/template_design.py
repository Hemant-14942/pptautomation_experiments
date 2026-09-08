"""
Fixed green-template design rules.

Only two template slides are scanned for cloneable shapes and colors:
  - second-to-last: MCQ question pill + A/B/C/D options
  - last: title banner, icon, background, body text color

Typography (font family and sizes) is fixed by the design team; the scanner
only supplies colors and shape XML to clone.
"""

# 0-based slide indices; negative counts from the end of the deck.
MCQ_DESIGN_SLIDE_INDEX = -2
TITLE_DESIGN_SLIDE_INDEX = -1

# Every output slide reuses this template slide's layout shell and background.
OUTPUT_TEMPLATE_SLIDE_INDEX = -1

FIXED_FONT = "Cambria"
FIXED_HEADING_FONT_PT = 80
FIXED_BODY_FONT_PT = 50


def resolve_slide_index(index: int, slide_count: int) -> int:
    """Convert a 0-based or negative index into a valid slide index."""
    if slide_count <= 0:
        return 0
    if index < 0:
        index = slide_count + index
    return max(0, min(index, slide_count - 1))
