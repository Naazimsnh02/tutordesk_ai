"""FLUX client — diagram / illustration generation (Feature 4, Black Forest Labs claim).

Self-hosted on Modal (FLUX.1-schnell, Apache-2.0). Generates labeled science diagrams,
geometry figures, and picture-question art embedded in worksheet PDFs.
Skipped in Off-the-Grid mode (worksheets render text-only).
"""
from __future__ import annotations

import io
from functools import lru_cache

from PIL import Image

from config import CONFIG


@lru_cache(maxsize=1)
def _backend():
    import modal

    Flux = modal.Cls.from_name(CONFIG.modal_app_name, "Flux")
    return Flux()


def generate_diagram(prompt: str) -> Image.Image | None:
    """Return a PIL Image for `prompt`, or None if unavailable (offline / error)."""
    if CONFIG.offline:
        return None
    try:
        raw: bytes = _backend().generate_diagram.remote(prompt)
        return Image.open(io.BytesIO(raw))
    except Exception:
        return None
