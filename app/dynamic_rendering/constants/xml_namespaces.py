"""
XML namespace URLs used inside every .pptx file.

PowerPoint stores slides as XML. Tags like p:sp are not plain names —
they belong to a namespace (a long URL). lxml needs the full URL to find nodes.
"""

# Map short prefix → full namespace URL used in Office Open XML.
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",       # drawing: colors, text, geometry
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",  # presentation: slides, shapes
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",  # links to images, layouts
}

# Shorthand so we do not repeat NS["a"] everywhere.
A = NS["a"]  # drawing namespace
P = NS["p"]  # presentation namespace
R = NS["r"]  # relationships namespace

# When we change a shape's fill, we must remove ALL of these child tags first.
# Otherwise old fill types can stay and PowerPoint shows the wrong color.
#
# Example inside p:spPr:
#   a:solidFill     ← solid color fill
#   a:gradFill      ← gradient fill
#   a:blipFill      ← picture fill
FILL_TAGS = {"noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill"}