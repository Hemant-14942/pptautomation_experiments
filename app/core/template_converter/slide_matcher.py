"""Decides which template slide each input slide's layout should be
re-styled onto: one Azure/Claude call per deck (see
app/prompts/slide_matching_prompts.py), falling back to a local scoring
heuristic if that call fails or returns something unparseable.
"""
from __future__ import annotations

import json
from typing import Any

from app.ai.azure_ai_client import chat
from app.core.style_parser import SlideDesign
from app.prompts.slide_matching_prompts import (
    SLIDE_MATCHING_SYSTEM_PROMPT,
    build_slide_matching_prompt,
)


def heuristic_match(inputs: list[dict[str, Any]], designs: list[SlideDesign]) -> dict[int, int]:
    out: dict[int, int] = {}
    for info in inputs:
        sig = {"table_count": 0, "picture_count": 0, "group_count": 0, "has_question_badge": False}
        for it in info["items"]:
            if it["kind"] == "table":
                sig["table_count"] += 1
            elif it["kind"] == "picture":
                sig["picture_count"] += 1
            elif it["kind"] == "option" and it["grouped"]:
                sig["group_count"] += 1
            elif it["kind"] == "heading":
                sig["has_question_badge"] = True
        best = 0
        best_score = -1
        for di, d in enumerate(designs):
            score = 0
            if sig["table_count"] > 0 and d.fingerprint["table_count"] > 0:
                score += 5
            if sig["picture_count"] > 0 and d.fingerprint["picture_count"] > 0:
                score += 5
            if sig["has_question_badge"] and d.fingerprint["has_question_badge"]:
                score += 4
            if sig["group_count"] >= 2 and d.fingerprint["option_pills"] >= 2:
                score += 3
            if score > best_score:
                best_score = score
                best = di
        out[info["index"]] = best
    return out


def ask_azure_for_plan(
    inputs: list[dict[str, Any]],
    input_signatures: list[dict[str, Any]],
    designs: list[SlideDesign],
    deployment: str | None = None,
) -> dict[int, int]:
    prompt = build_slide_matching_prompt(input_signatures, designs)
    try:
        response = chat(prompt=prompt, deployment=deployment, max_tokens=2048, system=SLIDE_MATCHING_SYSTEM_PROMPT)
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            parsed = json.loads(text[json_start : json_end + 1])
            return {int(k): int(v) for k, v in parsed.items()}
    except Exception as exc:
        print(f"[azure-ai] fallback to heuristic ({exc})")
    return heuristic_match(inputs, designs)
