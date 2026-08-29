"""OOXML/DrawingML namespace URIs shared by every module that reads or
writes raw slide XML (app/core/design_spec.py, app/core/style_parser.py,
app/core/template_converter/*).

Single source of truth: previously each of those files declared its own
copy of this same dict.
"""

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
A = NS["a"]
P = NS["p"]
R = NS["r"]

# <p:spPr>/<p:grpSpPr> child tags that represent a fill -- collected here so
# "replace this shape's fill" logic always clears every fill variant instead
# of just the one the author happened to test with.
FILL_TAGS = {"noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill"}
