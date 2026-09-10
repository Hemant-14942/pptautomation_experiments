"""Fit-layout: slide detection, signatures, and per-type formatters."""

from app.dynamic_rendering.services.format_layout.detection.slide_type_detector import (
    detect_slide_type,
)
from app.dynamic_rendering.services.format_layout.registry import format_slide
from app.dynamic_rendering.services.format_layout.slide_signature import (
    parse_input_slide_signature,
)

__all__ = ["detect_slide_type", "format_slide", "parse_input_slide_signature"]
