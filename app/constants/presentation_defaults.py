"""Fallback PowerPoint presentation-level values, used by
app/core/template_converter/zip_assembly.py when the template's own
ppt/presentation.xml doesn't specify them (or is missing entirely).

Defaults match PowerPoint's own standard 16:9 EMU canvas.
"""

DEFAULT_SLIDE_WIDTH = 12_192_000
DEFAULT_SLIDE_HEIGHT = 6_858_000
DEFAULT_NOTES_WIDTH = 6_858_000
DEFAULT_NOTES_HEIGHT = 9_144_000

# Starting counters for ids minted while assembling the output deck -- kept
# high/sparse so they can't collide with ids already used by the cloned
# template shapes (which typically start low, e.g. from 2).
FIRST_SLIDE_ID = 256
FIRST_SHAPE_ID_PER_SLIDE = 9000
