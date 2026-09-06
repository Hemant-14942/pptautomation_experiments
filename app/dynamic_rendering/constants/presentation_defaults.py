"""
Fallback deck-level settings when building the output .pptx.

Used when reading/writing ppt/presentation.xml (slide list, slide size, notes size).
Also holds starting IDs for new slides and shapes so we do not reuse template IDs.
"""

# Standard 16:9 slide size in EMU (914400 EMU = 1 inch).
# XML location: ppt/presentation.xml → p:sldSz cx="..." cy="..."
# 914400 EMU = 1 inch.
EMU_PER_INCH = 914400
# XML: ppt/presentation.xml → <p:sldSz cx="..." cy="..." />
DEFAULT_SLIDE_WIDTH = 36_576_000   # 40.0 inches
DEFAULT_SLIDE_HEIGHT = 20_574_000  # 22.5 inches
# Aspect ratio: 40 / 22.5 = 16:9

# Notes page size (speaker notes view) — same units.
# XML location: ppt/presentation.xml → p:notesSz
DEFAULT_NOTES_WIDTH = 6_858_000
DEFAULT_NOTES_HEIGHT = 9_144_000

# First slide id when we build a new p:sldIdLst for the output deck.
# Start high so we do not collide with ids already in the template.
FIRST_SLIDE_ID = 256

# First shape id on each output slide (p:cNvPr id="...").
# Template shapes often use low ids like 2, 3 — we start at 9000 to stay safe.
FIRST_SHAPE_ID_PER_SLIDE = 9000