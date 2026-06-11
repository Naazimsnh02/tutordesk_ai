"""Feature 1 — Worksheet-from-Textbook (claims OpenBMB).

Chapter photo/PDF -> MiniCPM-V extracts content -> reuse the weekly-pack pipeline.
"""
from __future__ import annotations

from PIL import Image

from models.minicpm import read_image
from pipelines.weekly_pack import TeachingPack, build_pack
from utils.image import pdf_to_images

_EXTRACT = "Transcribe this textbook page: all text, headings, and describe any diagrams."


def from_image(image: Image.Image, *, grade: int, subject: str, **kwargs) -> TeachingPack:
    chapter_text = read_image(image, _EXTRACT)
    return build_pack(chapter_text, grade=grade, subject=subject, **kwargs)


def from_pdf(pdf_path: str, *, grade: int, subject: str, **kwargs) -> TeachingPack:
    pages = pdf_to_images(pdf_path)
    chapter_text = "\n".join(read_image(p, _EXTRACT) for p in pages)
    return build_pack(chapter_text, grade=grade, subject=subject, **kwargs)
