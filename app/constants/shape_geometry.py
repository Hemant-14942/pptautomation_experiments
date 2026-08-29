"""Geometry thresholds used to recognize shape *roles* (heading pill, MCQ
option pill, logo, title banner, ...) purely from size/position -- both when
scanning a template (app/core/design_spec.py) and when classifying an input
deck's shapes (app/core/template_converter/shape_collector.py).

All linear values are EMU (English Metric Units, 914400 per inch) unless a
name says otherwise.
"""

# --- absolute-size buckets (fixed-canvas templates) ------------------------
# "pill + overlaid label" vocabulary: a compact MCQ heading badge.
HEADING_CX = (5_000_000, 9_500_000)
HEADING_CY = (1_000_000, 2_300_000)

# A per-option (A/B/C/D) circular pill.
OPTION_CX = (1_200_000, 2_100_000)
OPTION_CY = (1_200_000, 2_100_000)

# A brand logo picture.
LOGO_CX = (300_000, 3_200_000)
LOGO_CY = (300_000, 3_200_000)

# --- fraction-of-slide-size buckets (scales with oversized canvases, e.g. -
# --- Google Slides' 4x export) ----------------------------------------------
# A near-full-width (or wider) rounded banner used on topic-title slides,
# paired with a corner icon graphic -- distinct from the compact heading
# pill above, whose absolute-EMU bucket would false-negative on such decks.
TITLE_BANNER_WIDTH_FRACTION = 0.35
ICON_ZONE_X_FRACTION = 0.35
ICON_MAX_SIZE_FRACTION = 0.30

# --- matching tolerances ----------------------------------------------------
# Max offset (EMU) between two shapes' positions for them to be treated as
# "the same rect" -- e.g. detecting a cloned logo already on a slide.
RECTS_CLOSE_TOLERANCE = 200_000
LOGO_DUPLICATE_POSITION_TOLERANCE = 10_000_000
LOGO_DUPLICATE_SIZE_TOLERANCE = 1_500_000
LOGO_RECLONE_TOLERANCE = 300_000

# Max distance (EMU) between a roundRect pill and its paired label shape for
# them to be matched positionally (as opposed to by document order).
LABEL_PAIRING_TOLERANCE = 500_000
