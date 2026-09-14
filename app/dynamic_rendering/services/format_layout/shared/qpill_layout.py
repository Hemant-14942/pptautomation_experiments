"""Shared question-pill geometry used by all qpill slide types."""

QUESTION_PILL = {
    "x": -1_864_528,
    "y": 681_774,
    "width": 7_081_988,
    "height": 1_569_660,
}

QUESTION_LABEL = {
    "x": 1_039_500,
    "y": 827_049,
    "width": 4_562_190,
    "height": 1_015_622,
}


def question_pill_for(dspec=None) -> dict:
    y = QUESTION_PILL["y"]
    if dspec is not None and dspec.has_top_banner():
        y = dspec.y_below_banner(y)
    return {**QUESTION_PILL, "y": y}


def question_label_for(dspec=None) -> dict:
    y = QUESTION_LABEL["y"]
    if dspec is not None and dspec.has_top_banner():
        y = dspec.y_below_banner(y)
    return {**QUESTION_LABEL, "y": y}
