"""Prompt for the once-per-template Azure/Claude call that normalizes the
heuristically-scanned design tokens (heading/option pill colors, fonts,
table styling) into a strict JSON schema.

Call site: app/core/design_spec.py (_ask_azure_for_tokens). On failure the
caller keeps the raw heuristic tokens -- this call only confirms/cleans them
up, it never invents values the heuristic scan didn't already observe.
"""
from __future__ import annotations

import json
from typing import Any

DESIGN_TOKENS_SYSTEM_PROMPT = (
    "You are a presentation design analyst. You are given colors and "
    "fonts that were heuristically extracted from a PowerPoint "
    "template's heading pill, per-option (A/B/C/D) pills, and table "
    "styling. Normalize and confirm them into STRICT JSON matching "
    "exactly this schema, with no commentary, no markdown, JSON only:\n"
    '{"heading_pill": {"fill": "#RRGGBB", "text_color": "#RRGGBB", "font": "..."}, '
    '"option_pills": {"A": "#RRGGBB", "B": "#RRGGBB", "C": "#RRGGBB", "D": "#RRGGBB"} '
    'or {"shared": "#RRGGBB"} if every option pill shares one color, '
    '"table": {"header_fill": "#RRGGBB", "border": "#RRGGBB", "text_color": "#RRGGBB"}, '
    '"accent": "#RRGGBB"}\n'
    "Only reuse colors present in the extracted data below -- do not "
    "invent new brand colors that were not observed."
)


def build_design_tokens_prompt(heuristic_tokens: dict[str, Any]) -> str:
    return "Extracted template design tokens:\n" + json.dumps(heuristic_tokens, indent=2)
