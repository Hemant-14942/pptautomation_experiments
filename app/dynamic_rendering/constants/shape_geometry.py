"""
Size and position thresholds for recognizing shape roles.

We do not read shape names like "Question" only — we also check width/height.
All sizes below are in EMU unless the name says FRACTION.
914400 EMU = 1 inch.
"""

# --- MCQ "Question" pill (small wide rounded rectangle) -------------------
# Typical XML: p:sp with a:prstGeom prst="roundRect"
HEADING_CX = (5_000_000, 9_500_000)   # width ~5.5" to ~10.4"
HEADING_CY = (1_000_000, 2_300_000)   # height ~1.1" to ~2.5"

# --- MCQ option pills A/B/C/D (small circles) -----------------------------
# Typical XML: p:sp with a:prstGeom prst="ellipse"
OPTION_CX = (1_200_000, 2_100_000)
OPTION_CY = (1_200_000, 2_100_000)

# --- Title banner (wide bar at top — fraction of slide, not fixed EMU) -----
# Used when slide is huge (e.g. Google Slides export).
TITLE_BANNER_WIDTH_FRACTION = 0.35   # shape width must be >= 35% of slide width
ICON_ZONE_X_FRACTION = 0.35          # icon must sit in left 35% of slide
ICON_MAX_SIZE_FRACTION = 0.30        # icon not bigger than 30% of slide width/height

# --- "Are these two shapes in the same place?" tolerances ------------------
RECTS_CLOSE_TOLERANCE = 200_000

# Max gap between pill and its label text shape when pairing them.
LABEL_PAIRING_TOLERANCE = 500_000

# --- Title heading auto-fit (long titles widen the banner) ----------------
TITLE_HEADING_RIGHT_MARGIN_FRACTION = 0.10   # leave 10% empty on right of slide
TITLE_HEADING_RIGHT_PADDING_FRACTION = 0.01 # small gap after text inside banner
TITLE_HEADING_AVG_CHAR_WIDTH_EM = 0.62      # rough guess: how wide each character is
EMU_PER_PT = 12700                            # convert font points to EMU
TITLE_HEADING_MIN_FONT_SCALE = 0.6          # shrink font to 60% max, not smaller
TITLE_HEADING_DEFAULT_FONT_PT = 40.0        # fallback if template has no font size

# Gap below title banner before body content starts (used when shifting shapes down).
# PILL_CONTENT_GAP = 500_000  # ~0.55 inch gap under title banner
# for fit layout, we don't want any gap below the title banner
PILL_CONTENT_GAP = 0
