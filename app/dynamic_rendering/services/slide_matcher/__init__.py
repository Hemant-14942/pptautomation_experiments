"""Slide matching — heuristic-only for now (AI stub in Session 12)."""

from app.dynamic_rendering.services.slide_matcher.heuristic import heuristic_match, test_plan


def get_slide_plan(
    inputs: list,
    designs: list,
    *,
    mode: str = "test",
) -> dict[int, int]:
    """
    Build input-index -> template-slide-index mapping.

    mode="test"  — all inputs use last template slide (matches old builder.py)
    mode="heuristic" — local fingerprint scoring
    """
    if mode == "heuristic":
        return heuristic_match(inputs, designs)
    return test_plan(inputs, designs)


__all__ = ["get_slide_plan", "heuristic_match", "test_plan"]
