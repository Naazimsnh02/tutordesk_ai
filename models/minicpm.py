"""MiniCPM-V client — reads textbook pages & answer sheets (OpenBMB).

Cloud mode: calls the Modal `MiniCPM` function. Offline: loads locally (llama.cpp/transformers).
Version selected by CONFIG.minicpm_model (4.5 default, 4.6 lightweight fallback).
"""
from __future__ import annotations

from functools import lru_cache

from PIL import Image

from config import CONFIG


@lru_cache(maxsize=1)
def _backend():
    """TODO Phase 2: return Modal MiniCPM handle (or local loader if CONFIG.offline)."""
    raise NotImplementedError("Phase 2: wire MiniCPM-V backend")


def read_image(image: Image.Image, instruction: str) -> str:
    """Run a vision instruction over an image.

    Used by worksheet_from_textbook (chapter) and auto_grade (answer sheet).
    """
    return _backend().read_image(image, instruction)
