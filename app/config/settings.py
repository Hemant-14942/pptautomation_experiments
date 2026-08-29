from pathlib import Path
import os
from dataclasses import dataclass

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "app" / "data"


@dataclass(frozen=True)
class Paths:
    input_dir: Path = DATA_DIR / "input"
    output_dir: Path = DATA_DIR / "output"
    templates_dir: Path = DATA_DIR / "templates"

    def ensure(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)