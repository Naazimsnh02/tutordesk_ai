"""FLUX client — diagram / illustration generation (Feature 4, Black Forest Labs claim).

Self-hosted on Modal (FLUX.1-schnell, Apache-2.0). Generates labeled science diagrams,
geometry figures, and picture-question art embedded in worksheet PDFs.
Skipped in Off-the-Grid mode (worksheets render text-only).
"""
from __future__ import annotations

from functools import lru_cache

from PIL import Image

from config import CONFIG


@lru_cache(maxsize=1)
def _backend():
    """TODO Phase 5: return Modal Flux handle."""
    raise NotImplementedError("Phase 5: wire FLUX backend")


def generate_diagram(prompt: str) -> Image.Image | None:
    """Return an illustration for `prompt`, or None if unavailable (offline)."""
    if CONFIG.offline:
        return None
    return _backend().generate_diagram(prompt)
