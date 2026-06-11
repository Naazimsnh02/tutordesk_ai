"""Print-ready PDF export — every teacher output should be printable.

Uses reportlab; optionally embeds FLUX diagrams (Feature 4).
"""
from __future__ import annotations

from PIL import Image


def to_pdf(title: str, body: str, *, images: list[Image.Image] | None = None, out_path: str) -> str:
    """Render `title` + `body` (+ optional images) to a printable PDF. TODO Phase 1."""
    raise NotImplementedError("Phase 1: implement reportlab PDF export")
