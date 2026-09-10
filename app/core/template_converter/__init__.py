"""Template-conversion pipeline: turn an input .pptx into a copy re-styled
with a template .pptx's visual language (colors, fonts, pill/badge shapes,
logo, table header styling).

Split by responsibility:
  * shape_collector -- classify the input deck's shapes into roles
  * shape_emitter    -- render each role using the template's own shapes
  * table_restyle    -- header-row restyling for carried-over tables
  * slide_matcher    -- decide which template slide each input slide reuses
  * zip_assembly      -- read/write the .pptx zip parts (slides, rels,
                          presentation.xml, [Content_Types].xml)
  * xml_utils        -- low-level shape-XML mutation helpers shared above
  * builder           -- orchestrates the pipeline end to end (build_deck)
"""

__all__ = ["build_deck"]


def __getattr__(name: str):
    # Lazy import so fit_layout formatters can import xml_utils without
    # loading azure / AI dependencies from builder.
    if name == "build_deck":
        from app.core.template_converter.builder import build_deck
        return build_deck
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
