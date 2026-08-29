"""Fallback design-token values used by app/core/design_spec.py when a
template's own heading pill / option pills / table styling can't be
heuristically detected (or the AI normalization call fails). Kept as named
constants instead of bare hex literals scattered through the scan logic.
"""

DEFAULT_HEADING_FILL = "015500"
DEFAULT_HEADING_TEXT_COLOR = "FFFFFF"
DEFAULT_FONT = "Arial"
DEFAULT_OPTION_TEXT_COLOR = "FFFFFF"
DEFAULT_TABLE_HEADER_FILL = "275317"
DEFAULT_TABLE_BORDER_COLOR = "000000"
DEFAULT_TABLE_HEADER_TEXT_COLOR = "FFFFFF"
DEFAULT_TABLE_BODY_TEXT_COLOR = "000000"
DEFAULT_ACCENT = "000000"

# Media file extensions the output zip's [Content_Types].xml must be able to
# declare a Default entry for (logo / title icon / carried-over pictures).
MEDIA_CONTENT_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
}
DEFAULT_MEDIA_CONTENT_TYPE = "application/octet-stream"
