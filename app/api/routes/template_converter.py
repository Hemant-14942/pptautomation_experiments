import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.schemas import ErrorResponse, TemplateConverterResponse
from app.config.settings import Paths
from app.core.template_converter.builder import build_deck


router = APIRouter(prefix="/template-converter", tags=["template-converter"])

ALLOWED_EXTS = {".pptx"}


@router.post(
    "",
    response_model=TemplateConverterResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input (bad extension, missing file)."},
        500: {"model": ErrorResponse, "description": "Conversion failed."},
    },
    summary="Convert an input deck into a styled output deck using a template",
)
def template_converter(  # `def`, not `async def` — FastAPI auto-runs sync handlers in a threadpool,
                         # which keeps the event loop free while build_deck does heavy IO.
    template: UploadFile = File(..., description="Template .pptx file"),
    deck: UploadFile = File(..., description="Input deck .pptx file"),
) -> TemplateConverterResponse:
    template_name = template.filename or "template.pptx"
    deck_name = deck.filename or "deck.pptx"

    _validate_ext(template_name, "template")
    _validate_ext(deck_name, "deck")

    paths = Paths()
    paths.ensure()

    out_name = f"template-converter-{Path(deck_name).stem}.pptx"
    out_path = paths.output_dir / out_name

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        tpl_path = td_path / f"template{Path(template_name).suffix.lower()}"
        in_path = td_path / f"deck{Path(deck_name).suffix.lower()}"

        with tpl_path.open("wb") as f:
            shutil.copyfileobj(template.file, f)
        with in_path.open("wb") as f:
            shutil.copyfileobj(deck.file, f)

        try:
            build_deck(str(in_path), str(tpl_path), str(out_path))
        except HTTPException:
            raise
        except Exception as exc:
            out_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail=f"build_deck failed: {exc}",
            ) from exc

    if not out_path.exists():
        raise HTTPException(
            status_code=500,
            detail="build_deck returned without producing an output file.",
        )

    return TemplateConverterResponse(
        output_path=str(out_path),
        output_filename=out_name,
        input_filename=deck_name,
        template_filename=template_name,
        size_bytes=out_path.stat().st_size,
    )


def _validate_ext(filename: str, field: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"{field} must have one of {sorted(ALLOWED_EXTS)} extension, got {ext!r}.",
        )