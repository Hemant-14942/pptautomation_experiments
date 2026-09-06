"""Shape emitters — clone template shapes and apply design spec styling."""

from app.dynamic_rendering.services.shape_emitters.body import emit_body
from app.dynamic_rendering.services.shape_emitters.branding import emit_logo, emit_question_icon
from app.dynamic_rendering.services.shape_emitters.heading import emit_heading, emit_title_heading
from app.dynamic_rendering.services.shape_emitters.option import emit_option
from app.dynamic_rendering.services.shape_emitters.picture import emit_picture

__all__ = [
    "emit_body",
    "emit_heading",
    "emit_logo",
    "emit_option",
    "emit_picture",
    "emit_question_icon",
    "emit_title_heading",
]
