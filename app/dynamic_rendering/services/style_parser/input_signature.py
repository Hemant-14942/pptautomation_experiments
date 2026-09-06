"""
Build a small fingerprint dict for each slide in the INPUT deck.

Used for slide matching (table slide → template table layout, etc.).
Uses python-pptx slide.shapes — not raw XML.
"""

from __future__ import annotations

from typing import Any

from pptx import Presentation


def parse_input_slide_signature(input_path: str) -> list[dict[str, Any]]:
    """
    For each input slide return counts: tables, pictures, option pills, etc.

    Example one entry:
      {"index": 0, "table_count": 1, "picture_count": 0, "has_question_badge": True, ...}
    """
    # open input pptx
    prs = Presentation(input_path)
    sigs: list[dict[str, Any]] = []

    # loop slides by index 0, 1, 2, ...
    for idx, slide in enumerate(prs.slides):
        text_count = 0
        group_count = 0
        table_count = 0
        picture_count = 0
        option_pill_count = 0
        question_badge = False
        body_text_count = 0
        sample = ""

        # loop each top-level shape on slide
        for sp in slide.shapes:
            tag = sp.shape_type

            # groups have shape_type None in python-pptx
            if tag is None:
                group_count += 1
                try:
                    cw = sp.width or 0
                    ch = sp.height or 0
                    # tiny groups ≈ MCQ option pills
                    if cw and ch and cw < 2000000 and ch < 2000000:
                        option_pill_count += 1
                except Exception:
                    pass
                continue

            # count tables
            if hasattr(tag, "name") and tag.name == "TABLE":
                table_count += 1
            # count pictures
            elif hasattr(tag, "name") and tag.name == "PICTURE":
                picture_count += 1
            # count text shapes
            elif sp.has_text_frame:
                text_count += 1
                txt = sp.text_frame.text.strip().lower()
                # keep first snippet as sample text
                if not sample:
                    sample = sp.text_frame.text.strip()[:120]
                # detect "question" badge text
                if "question" in txt or "questions" in txt:
                    question_badge = True
                # long text ≈ body paragraph
                if len(txt) > 30:
                    body_text_count += 1

        # append one signature dict for this slide
        sigs.append({
            "index": idx,
            "shape_count": len(slide.shapes),
            "text_count": text_count,
            "group_count": group_count,
            "table_count": table_count,
            "picture_count": picture_count,
            "option_pills": option_pill_count,
            "has_question_badge": question_badge,
            "body_text_count": body_text_count,
            "sample": sample,
        })

    return sigs