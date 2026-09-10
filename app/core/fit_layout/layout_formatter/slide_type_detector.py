from typing import Any

from pptx.presentation import Presentation as PresentationType
from pptx.slide import Slide

from app.core.slide_text_analyzer import extract_text_from_slide

SLIDE_TYPE_TITLE_TABLE_ONLY = "title_table_only"
SLIDE_TYPE_TITLE_BODY_ONLY = "title_body_only"
SLIDE_TYPE_TITLE_BODY_SINGLE_IMAGE = "title_body_single_image"
SLIDE_TYPE_TITLE_BODY_MULTIPLE_IMAGES = "title_body_multiple_images"
SLIDE_TYPE_TITLE_IMAGE_ONLY = "title_image_only"

# Slide has ONLY body text — no heading, no image, no table, no MCQ options
SLIDE_TYPE_BODY_ONLY = "body_only"

# Slide has ONLY pictures — no heading, no body text, no table, no MCQ options
SLIDE_TYPE_IMAGE_ONLY = "image_only"

# Slide has ONLY a table — no heading, no body text, no images, no question pill
SLIDE_TYPE_TABLE_ONLY = "table_only"

# Question-based slide types (no title heading required)
SLIDE_TYPE_QUESTION_QTEXT_MCQ = "question_qtext_mcq"
SLIDE_TYPE_QPILL_QTEXT_TABLE_MCQ = "qpill_qtext_table_mcq"
SLIDE_TYPE_QPILL_QTEXT_ONLY = "qpill_qtext_only"
SLIDE_TYPE_QPILL_QTEXT_IMAGE_MCQ = "qpill_qtext_image_mcq"

# Pictures at or above this Y position are treated as header logos/icons,
# not content images. Fixed value, not per-slide dynamic — chosen from
# observed logo positions (~0.94-0.95in) vs heading text start (~1.7in) in
# sample input decks (see app/data/input/p1.pptx).
IMAGE_Y_THRESHOLD_EMU = 1_828_800  # 2.0 inches


def has_real_body_text(slide: Slide, heading_pos: tuple[int, int] | None) -> bool:
    """Any text shape with >30 chars of content, excluding the heading's
    own shape (matched by position) so a long heading is never
    double-counted as body text too."""
    for sp in slide.shapes:
        if not sp.has_text_frame:
            continue
        if heading_pos is not None and (sp.left, sp.top) == heading_pos:
            continue
        if len(sp.text_frame.text.strip()) > 30:
            return True
    return False


def count_real_images(slide: Slide) -> int:
    """Count PICTURE shapes positioned below the header area.

    Excludes logos/icons placed near the top of the slide, which
    parse_input_slide_signature's picture_count does not distinguish from
    actual content images.
    """
    count = 0
    for sp in slide.shapes:
        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "PICTURE":
            if sp.top is not None and sp.top > IMAGE_Y_THRESHOLD_EMU:
                count += 1
    return count


def count_actual_tables(slide: Slide) -> int:
    """Count TABLE shapes in the slide by checking actual shape type.

    Does NOT rely on parse_input_slide_signature which may be inaccurate.
    Directly counts shapes with type == TABLE (19).

    Returns:
        Number of TABLE shapes found in the slide
    """
    # Count by directly checking shape types
    table_count = 0
    for sp in slide.shapes:
        # Check if shape type is TABLE
        shape_type = sp.shape_type
        if shape_type is not None and getattr(shape_type, "name", "") == "TABLE":
            table_count += 1

    return table_count


def has_question_pill(slide: Slide) -> bool:
    """True if the slide has a roundRect shape (the green Question pill at top)."""
    from app.constants.xml_namespaces import NS

    for sp in slide.shapes:
        if not hasattr(sp, "_element"):
            continue
        geom = sp._element.find(".//{%s}prstGeom" % NS["a"])
        if geom is not None and geom.get("prst") == "roundRect":
            return True
    return False


def has_option_pill_shapes(slide: Slide) -> bool:
    """True if the slide has MCQ option pills (ellipses or option groups)."""
    from app.constants.xml_namespaces import NS

    for sp in slide.shapes:
        if str(sp.shape_type) == "<ShapeType.GROUP: 6>":
            return True
        if not hasattr(sp, "_element"):
            continue
        geom = sp._element.find(".//{%s}prstGeom" % NS["a"])
        if geom is not None and geom.get("prst") == "ellipse":
            return True
    return False


def has_any_text_content(slide: Slide) -> bool:
    """True if ANY shape on the slide has non-empty text (even 1 character)."""
    for sp in slide.shapes:
        if sp.has_text_frame and sp.text_frame.text.strip():
            return True
    return False


def _no_title_or_question_layout(
    slide: Slide, prs: PresentationType, signature: dict[str, Any]
) -> bool:
    """True when slide has no heading pill and no question/MCQ layout."""
    if extract_text_from_slide(slide, 0, prs).get("heading") is not None:
        return False
    if signature.get("option_pills", 0) > 0:
        return False
    if has_question_pill(slide):
        return False
    if has_option_pill_shapes(slide):
        return False
    if has_mcq_structure(slide):
        return False
    return True


def qualifies_for_pure_slide(slide: Slide, prs: PresentationType, signature: dict[str, Any]) -> bool:
    """Shared gate for body_only and image_only.

    Both types mean the slide has ONLY one kind of content — nothing else:
      - NO title heading (green heading pill)
      - NO table
      - NO question pill (roundRect)
      - NO MCQ option pills (ellipses / groups)
      - NO full MCQ layout
    """
    if not _no_title_or_question_layout(slide, prs, signature):
        return False
    if count_actual_tables(slide) > 0:
        return False
    return True


def qualifies_for_table_only_slide(
    slide: Slide, prs: PresentationType, signature: dict[str, Any]
) -> bool:
    """Gate for table_only — slide has ONLY one table, nothing else.

      - NO title heading
      - NO standalone text boxes (text inside table cells is OK)
      - NO content images
      - NO question pill / MCQ
      - exactly ONE table on the slide
    """
    if not _no_title_or_question_layout(slide, prs, signature):
        return False
    if count_real_images(slide) > 0:
        return False
    if has_any_text_content(slide):
        return False
    return count_actual_tables(slide) == 1


def has_mcq_structure(slide: Slide) -> bool:
    """Check if slide has MCQ structure: question pill + 4 option pills (ellipses).

    MCQ slides have:
    - 1 roundRect shape (question pill at top)
    - 4 ellipse shapes (MCQ option pills A, B, C, D)
    - Multiple text boxes (question text + option labels + answer text)
    - NO title heading (these are question-based, not title-based)
    - NO tables, NO images

    Returns:
        True if slide has MCQ structure (1+ roundRect + 4 ellipses), False otherwise
    """
    from lxml import etree

    from app.constants.xml_namespaces import NS

    # Count roundRect and ellipse shapes
    roundrect_count = 0
    ellipse_count = 0

    for sp in slide.shapes:
        # For shapes that are direct shape elements (not groups)
        if hasattr(sp, "_element"):
            elem = sp._element

            # Find preset geometry to identify shape type
            geom = elem.find(
                ".//{%s}prstGeom" % NS["a"]
            )  # Look for <a:prstGeom> elements

            if geom is not None:
                prst = geom.get("prst")  # Get preset geometry name
                if prst == "roundRect":  # Question pill is roundRect
                    roundrect_count += 1
                elif prst == "ellipse":  # MCQ options are ellipses
                    ellipse_count += 1

        # Also check groups (MCQ options might be grouped)
        if str(sp.shape_type) == "<ShapeType.GROUP: 6>":
            # Groups might contain ellipse shapes
            # Count groups as potential option containers
            ellipse_count += 1

    # MCQ structure: 1 roundRect (question pill) + 4 ellipses (option pills)
    # We expect exactly 1 roundRect and at least 4 ellipses (or groups)
    has_mcq = roundrect_count >= 1 and ellipse_count >= 4

    return has_mcq


def qualifies_for_qpill_qtext_only_slide(
    slide: Slide, prs: PresentationType, signature: dict[str, Any]
) -> bool:
    """Gate for qpill_qtext_only — question pill + question text, nothing else.

      - NO title heading
      - question pill (roundRect) present
      - NO MCQ option pills
      - NO table
      - NO content images
      - at least one text box below the pill (len >= 1, not the "Question" label)
    """
    from app.core.fit_layout.layout_formatter.qpill_shape_utils import (
        has_question_text_below_pill,
    )

    if extract_text_from_slide(slide, 0, prs).get("heading") is not None:
        return False
    if not has_question_pill(slide):
        return False
    if has_mcq_structure(slide) or has_option_pill_shapes(slide):
        return False
    if count_actual_tables(slide) > 0:
        return False
    if count_real_images(slide) > 0:
        return False
    return has_question_text_below_pill(slide)


def detect_slide_type(
    signature: dict[str, Any], slide: Slide, prs: PresentationType
) -> str | None:

    # =========================================================================
    # SECTION 1: Check for MCQ slide type (question-based, no heading required)
    # =========================================================================
    # MCQ slides are question-based and don't have a title heading
    # They must have: 1 question pill (roundRect) + 4 option pills (ellipses)
    if has_mcq_structure(slide):
        # Confirm this is specifically question+text+mcq type (no table, no images)
        # Count actual TABLE shapes (not relying on signature which may be inaccurate)
        actual_table_count = count_actual_tables(slide)
        real_image_count = count_real_images(slide)

        if actual_table_count == 0 and real_image_count >= 1:
            # question + text + image + MCQ (e.g. ptest1.pptx slide 16)
            return SLIDE_TYPE_QPILL_QTEXT_IMAGE_MCQ
        if real_image_count == 0:
            # question + text + table + MCQ (e.g. p.pptx slide 0)
            if actual_table_count == 1:
                return SLIDE_TYPE_QPILL_QTEXT_TABLE_MCQ
            # question + text + MCQ, no table
            if actual_table_count == 0:
                return SLIDE_TYPE_QUESTION_QTEXT_MCQ

    # =========================================================================
    # SECTION 1b: question pill + text only (no table, no MCQ, no images)
    # =========================================================================
    if qualifies_for_qpill_qtext_only_slide(slide, prs, signature):
        return SLIDE_TYPE_QPILL_QTEXT_ONLY

    # =========================================================================
    # SECTION 2: table_only, body_only, or image_only (one content type only)
    # =========================================================================
    heading = extract_text_from_slide(slide, 0, prs).get("heading")
    has_heading = heading is not None
    no_options = signature.get("option_pills", 0) == 0
    table_count = signature.get("table_count", 0)
    actual_table_count = count_actual_tables(slide)
    real_image_count = count_real_images(slide)

    if qualifies_for_table_only_slide(slide, prs, signature):
        return SLIDE_TYPE_TABLE_ONLY

    if qualifies_for_pure_slide(slide, prs, signature):
        # image_only: pictures ONLY — not a single text box anywhere on slide
        if real_image_count >= 1 and not has_any_text_content(slide):
            return SLIDE_TYPE_IMAGE_ONLY
        # body_only: body text ONLY — no pictures anywhere on slide
        if real_image_count == 0 and has_real_body_text(slide, None):
            return SLIDE_TYPE_BODY_ONLY

    # =========================================================================
    # SECTION 3: title-based slide types (all require a heading pill)
    # =========================================================================
    # Title-based slides need BOTH a heading AND no MCQ option pills
    if not (has_heading and no_options):
        return None

    # Get heading position so we don't count the heading text as body text
    heading_pos = heading.get("position_top_left")
    has_body = has_real_body_text(slide, heading_pos)

    # Check for title_table_only: heading + 1 table, no body, no images
    if table_count == 1 and not has_body and real_image_count == 0:
        return SLIDE_TYPE_TITLE_TABLE_ONLY

    # heading + images only (no body text, no table) — e.g. ptest1 slides 18-19
    if table_count == 0 and not has_body and real_image_count >= 1:
        return SLIDE_TYPE_TITLE_IMAGE_ONLY

    # Check for body-based slides (title_body_only, _single_image, _multiple_images)
    if table_count == 0 and has_body:
        if real_image_count == 0:
            return SLIDE_TYPE_TITLE_BODY_ONLY
        elif real_image_count == 1:
            return SLIDE_TYPE_TITLE_BODY_SINGLE_IMAGE
        elif real_image_count >= 2:
            return SLIDE_TYPE_TITLE_BODY_MULTIPLE_IMAGES

    # No matching type found
    return None
