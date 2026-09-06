"""Data objects passed between services (no file I/O here)."""

from app.dynamic_rendering.domain.models.design_spec import DesignSpec
from app.dynamic_rendering.domain.models.slide_design import ShapeStyle, SlideDesign

__all__ = ["DesignSpec", "ShapeStyle", "SlideDesign"]