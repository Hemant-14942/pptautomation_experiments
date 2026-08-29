"""Prompt for the single per-deck Azure/Claude call that maps each input
slide to the template slide whose layout it should be re-styled onto.

Call site: app/core/template_converter/slide_matcher.py
On failure (bad response, no credentials, ...) the caller falls back to
`_heuristic_match`, a purely local scoring heuristic -- so this prompt only
needs to *improve* on that heuristic, not be relied on.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.core.style_parser import SlideDesign

SLIDE_MATCHING_SYSTEM_PROMPT = (
    "You are a slide-layout classifier. Given a list of input slides "
    "and a list of template slides, output ONLY a JSON object mapping "
    "every input slide index (0-based) to the 0-based template slide "
    "index that best matches its layout role. Use the template's role "
    "distribution (heading, question_badge, option_pill, table, body) "
    "as the matching key. No commentary, no markdown, no prose. JSON only."
)


def _format_template_designs(designs: list["SlideDesign"]) -> str:
    lines = []
    for d in designs:
        role_counts: dict[str, int] = {}
        for s in d.shapes:
            role_counts[s.role] = role_counts.get(s.role, 0) + 1
        lines.append(
            f"Template slide {d.index+1}: bg={d.background_kind}, "
            f"theme_font={d.theme_font!r}, shapes={role_counts}, "
            f"layout={d.layout_name!r}"
        )
    return "\n".join(lines)


def build_slide_matching_prompt(
    input_signatures: list[dict[str, Any]],
    designs: list["SlideDesign"],
) -> str:
    """User-turn text: a plain-text structural signature for every input
    slide, paired with the same summary for every template slide."""
    input_lines = [
        f"Input slide {sig['index']}: "
        f"shape_count={sig['shape_count']}, text={sig['text_count']}, "
        f"groups(option_pills)={sig['group_count']}, tables={sig['table_count']}, "
        f"pictures={sig['picture_count']}, has_question_badge={sig['has_question_badge']}, "
        f"sample={sig['sample']!r}"
        for sig in input_signatures
    ]
    return (
        "INPUT SLIDES:\n" + "\n".join(input_lines)
        + "\n\nTEMPLATE SLIDES:\n" + _format_template_designs(designs)
        + "\n\nRespond with JSON only, e.g. {\"0\": 1, \"1\": 3, ...}"
    )
