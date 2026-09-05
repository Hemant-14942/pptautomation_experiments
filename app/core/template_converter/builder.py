from __future__ import annotations

import os
import zipfile
from pathlib import Path

from app.core.design_spec import get_design_spec
from app.core.style_parser import parse_input_slide_signature, parse_template
from app.core.template_converter.shape_collector import collect_inputs
from app.core.template_converter.slide_matcher import ask_azure_for_plan
from app.core.template_converter.zip_assembly import build_output, read_template_archive


def build_deck(input_path: str, template_path: str, output_path: str) -> None:
    print(f"[builder] input    = {input_path}")
    print(f"[builder] template = {template_path}")
    print(f"[builder] output   = {output_path}")

    template_parts, template_slide_xmls, template_layout_rids = read_template_archive(template_path)
    _, designs, _ = parse_template(template_path)
    input_signatures = parse_input_slide_signature(input_path)

    dspec = get_design_spec(template_path)
    print(
        f"[builder] design spec (source={dspec.source}): heading_fill=#{dspec.heading_fill} "
        f"option_fill={dspec.option_fill} table_header_fill=#{dspec.table_header_fill} "
        f"logo={'yes' if dspec.logo_el is not None else 'no'} "
        f"title_banner={'yes' if dspec.title_banner_el is not None else 'no'} "
        f"title_icon={'yes' if dspec.title_icon_el is not None else 'no'}"
    )

    # dspec is passed in so shapes matching the template's title-banner
    # pattern can be classified accordingly instead of falling through as
    # generic body content.
    inputs = collect_inputs(input_path, dspec)

    print(f"[builder] template slides: {len(designs)} | input slides: {len(inputs)}")

    last = len(designs) - 1
    plan = {info["index"]: last for info in inputs}
    print(f"[builder] TEST plan (all -> last template slide {last}): {plan}")
    # plan = ask_azure_for_plan(inputs, input_signatures, designs)
    # print(f"[builder] azure plan: {plan}")

    out_parts = build_output(
        template_parts, template_slide_xmls, template_layout_rids,
        designs, inputs, plan, dspec,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, blob in out_parts.items():
            zf.writestr(name, blob)
    print(f"[builder] wrote {output_path} ({os.path.getsize(output_path)} bytes)")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: builder.py <input.pptx> <template.pptx> <output.pptx>")
        sys.exit(1)
    build_deck(sys.argv[1], sys.argv[2], sys.argv[3])
