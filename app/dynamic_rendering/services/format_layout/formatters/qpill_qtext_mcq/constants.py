"""Fixed layout for question pill + text + four MCQ options."""

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

QUESTION_TEXT = {
    "x": 1_104_806,
    "y": 2_396_709,
    "width": 34_747_200,
    "height": 4_389_120,
}

OPTION_A_PILL = {
    "x": 1_039_499,
    "y": 8_105_829,
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_A_LABEL = {
    "x": 1_104_807,
    "y": 8_304_334,
    "width": 1_466_700,
    "height": 1_169_511,
}

OPTION_A_TEXT = {
    "x": 3_107_605,
    "y": 8_396_618,
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_B_PILL = {
    "x": 1_039_499,
    "y": 10_223_169,
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_B_TEXT = {
    "x": 3_107_605,
    "y": 10_453_760,
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_C_PILL = {
    "x": 1_039_499,
    "y": 12_340_509,
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_C_TEXT = {
    "x": 3_107_605,
    "y": 12_521_075,
    "width": 32_744_401,
    "height": 1_597_340,
}

OPTION_D_PILL = {
    "x": 1_039_499,
    "y": 14_457_849,
    "width": 1_597_200,
    "height": 1_597_200,
}

OPTION_D_TEXT = {
    "x": 3_107_605,
    "y": 14_656_354,
    "width": 32_744_401,
    "height": 1_597_340,
}

MCQ_OPTIONS = [
    {"label": "A", "pill": OPTION_A_PILL, "label_box": OPTION_A_LABEL, "text_box": OPTION_A_TEXT},
    {"label": "B", "pill": OPTION_B_PILL, "label_box": None, "text_box": OPTION_B_TEXT},
    {"label": "C", "pill": OPTION_C_PILL, "label_box": None, "text_box": OPTION_C_TEXT},
    {"label": "D", "pill": OPTION_D_PILL, "label_box": None, "text_box": OPTION_D_TEXT},
]
