"""Top-level pipeline: input deck + template -> styled output deck."""

from __future__ import annotations

import os

from app.dynamic_rendering.infrastructure.pptx.archive_reader import read_template_archive
from app.dynamic_rendering.infrastructure.pptx.archive_writer import write_archive
from app.dynamic_rendering.services.design_spec import get_design_spec
from app.dynamic_rendering.services.input_collector import collect_inputs
from app.dynamic_rendering.services.output_assembler import build_output
from app.dynamic_rendering.services.slide_matcher import get_slide_plan
from app.dynamic_rendering.services.style_parser.template_parser import parse_template


def build_deck(
    input_path: str,
    template_path: str,
    output_path: str,
    *,
    slide_plan_mode: str = "test",
) -> None:
    print(f"[builder] input    = {input_path}")
    print(f"[builder] template = {template_path}")
    print(f"[builder] output   = {output_path}")

    archive = read_template_archive(template_path)
    _, designs, _ = parse_template(template_path)
    dspec = get_design_spec(template_path)
    print(
        f"[builder] design spec (source={dspec.source}): heading_fill=#{dspec.heading_fill} "
        f"option_fill={dspec.option_fill} table_header_fill=#{dspec.table_header_fill} "
        f"logo={'yes' if dspec.logo_el is not None else 'no'} "
        f"title_banner={'yes' if dspec.title_banner_el is not None else 'no'} "
        f"title_icon={'yes' if dspec.title_icon_el is not None else 'no'}"
    )

    inputs = collect_inputs(input_path, dspec)
    print(f"[builder] template slides: {len(designs)} | input slides: {len(inputs)}")

    plan = get_slide_plan(inputs, designs, mode=slide_plan_mode)
    if slide_plan_mode == "test" and designs:
        last = len(designs) - 1
        print(f"[builder] TEST plan (all -> last template slide {last}): {plan}")
    else:
        print(f"[builder] slide plan ({slide_plan_mode}): {plan}")

    out_parts = build_output(
        archive.parts,
        archive.slide_xmls,
        archive.layout_rids,
        designs,
        inputs,
        plan,
        dspec,
    )

    write_archive(out_parts, output_path)
    print(f"[builder] wrote {output_path} ({os.path.getsize(output_path)} bytes)")
