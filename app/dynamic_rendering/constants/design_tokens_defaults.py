"""
Default colors and fonts when the template scan finds nothing.

These are fallbacks only — real runs use colors scraped from the template.
Hex values are 6 chars without # (PowerPoint XML uses val=\"015500\").
"""

# MCQ question pill background and text (template family default green/white).
DEFAULT_QUESTION_PILL_FILL = "015500"
DEFAULT_QUESTION_PILL_TEXT_COLOR = "FFFFFF"
DEFAULT_FONT = "Cambria"
DEFAULT_HEADING_FONT_PT = 80

# Option pill letter text color (A/B/C/D labels).
DEFAULT_OPTION_TEXT_COLOR = "FFFFFF"

# Table header row styling when template table scan fails.
DEFAULT_TABLE_HEADER_FILL = "275317"
DEFAULT_TABLE_BORDER_COLOR = "000000"
DEFAULT_TABLE_HEADER_TEXT_COLOR = "FFFFFF"
DEFAULT_TABLE_BODY_TEXT_COLOR = "000000"

# Last-resort accent (option pill color if letter not in template map).
DEFAULT_ACCENT = "000000"

# When we add images to ppt/media/, [Content_Types].xml must declare each extension.
# Example: ppt/media/design_spec_title_icon.png needs Extension="png" ContentType="image/png"
MEDIA_CONTENT_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
}
DEFAULT_MEDIA_CONTENT_TYPE = "application/octet-stream"