"""Local slide-matching heuristics (no Azure AI)."""

from __future__ import annotations

from typing import Any

from app.dynamic_rendering.domain.models.slide_design import SlideDesign


def heuristic_match(inputs: list[dict[str, Any]], designs: list[SlideDesign]) -> dict[int, int]:
    """Score each input slide against template slide fingerprints."""
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


def test_plan(inputs: list[dict[str, Any]], designs: list[SlideDesign]) -> dict[int, int]:
    """Map every input slide to the last template slide (current builder TEST mode)."""
    if not designs:
        return {}
    last = len(designs) - 1
    return {info["index"]: last for info in inputs}
