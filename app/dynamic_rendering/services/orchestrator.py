"""Top-level pipeline: input deck + template -> styled output deck."""

from __future__ import annotations

import logging
import os

import app.dynamic_rendering.log  # noqa: F401 — configure ECS logging

from app.dynamic_rendering.infrastructure.pptx.archive_reader import read_template_archive
from app.dynamic_rendering.infrastructure.pptx.archive_writer import write_archive
from app.dynamic_rendering.services.design_spec import get_design_spec
from app.dynamic_rendering.services.input_collector import collect_inputs
from app.dynamic_rendering.services.output_assembler import build_output

logger = logging.getLogger(__name__)


def build_deck(input_path: str, template_path: str, output_path: str) -> None:
    logger.info("build started", extra={"input": input_path, "template": template_path, "output": output_path})

    archive = read_template_archive(template_path)
    dspec = get_design_spec(template_path)
    logger.info(
        "design spec loaded",
        extra={
            "source": dspec.source,
            "question_pill_fill": dspec.question_pill_fill,
            "option_fill": dspec.option_fill,
            "table_header_fill": dspec.table_header_fill,
            "title_banner": dspec.title_banner_el is not None,
            "title_icon": dspec.title_icon_el is not None,
        },
    )

    inputs = collect_inputs(input_path, dspec)
    logger.info(
        "inputs collected",
        extra={
            "output_shell": archive.output_shell_partname,
            "template_slide_count": archive.slide_count,
            "input_slide_count": len(inputs),
        },
    )

    out_parts = build_output(
        archive.parts,
        archive.output_shell_xml,
        archive.output_shell_partname,
        inputs,
        dspec,
    )

    write_archive(out_parts, output_path)
    logger.info("build finished", extra={"output": output_path, "bytes": os.path.getsize(output_path)})
