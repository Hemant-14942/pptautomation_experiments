"""Dev entry point — run the dynamic_rendering orchestrator with repo default paths."""

from __future__ import annotations

import app.dynamic_rendering.log  # noqa: F401 — configure ECS logging

from app.dynamic_rendering.config.settings import Paths
from app.dynamic_rendering.services.orchestrator import build_deck

IS_DEFENCE = True # True = defence layout (banner spacing); False = normal template


def run(
    input_path: str,
    template_path: str,
    output_path: str,
    is_defence: bool = False,
) -> None:
    print(f"Input:    {input_path}")
    print(f"Template: {template_path}")
    print(f"Output:   {output_path}")
    print(f"Defence:  {is_defence}")
    print()
    build_deck(input_path, template_path, output_path, is_defence=is_defence)


if __name__ == "__main__":
    paths = Paths()
    paths.ensure()

    run(
        input_path=str(paths.input_dir / "ptest1.pptx"),
        template_path=str(paths.templates_dir / "defence-red-final.pptx"),
        output_path=str(paths.output_dir / "test_ptest1.pptx"),
        is_defence=IS_DEFENCE,
    )

# command to run the script
# PYTHONPATH=. uv run python app/main.py
