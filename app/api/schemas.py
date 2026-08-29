from typing import Literal, Optional

from pydantic import BaseModel, Field


class TemplateConverterResponse(BaseModel):
    status: Literal["ok"] = "ok"
    output_path: str = Field(..., description="Absolute path of the generated .pptx on disk.")
    output_filename: str = Field(..., description="Just the filename of the generated deck.")
    input_filename: str = Field(..., description="Filename of the uploaded input deck.")
    template_filename: str = Field(..., description="Filename of the uploaded template deck.")
    size_bytes: int = Field(..., ge=0, description="Size of the generated deck in bytes.")


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    detail: str = Field(..., description="Human-readable error message.")
    code: Optional[str] = Field(
        default=None,
        description="Machine-readable error code (e.g. 'invalid_extension').",
    )
