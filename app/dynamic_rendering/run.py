"""Dev entry point — run the dynamic_rendering orchestrator with repo default paths."""

from __future__ import annotations

import app.dynamic_rendering.log  # noqa: F401 — configure ECS logging

from app.config.settings import Paths
from app.dynamic_rendering.services.orchestrator import build_deck


def run(input_path: str, template_path: str, output_path: str) -> None:
    print(f"Input:    {input_path}")
    print(f"Template: {template_path}")
    print(f"Output:   {output_path}")
    print()
    build_deck(input_path, template_path, output_path)


if __name__ == "__main__":
    paths = Paths()
    paths.ensure()

    run(
        input_path=str(paths.input_dir / "p2.pptx"),
        template_path=str(paths.templates_dir / "standard-red.pptx"),
        output_path=str(paths.output_dir / "standard-red_test.pptx"),
    )

# command to run the script
# PYTHONPATH=. uv run python app/dynamic_rendering/run.py
