from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]  # template-beautifier/
sys.path.insert(0, str(ROOT))

from app.core.slide_text_analyzer import analyze_slides_text

pptx = ROOT / "app/data/input/p5.pptx"
analyze_slides_text(str(pptx), 2, 6)

# run command for the file
# PYTHONPATH=. uv run python app/tests/slide_text_test.py