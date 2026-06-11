"""Image helpers: PDF rasterization and basic preprocessing for vision input."""
from __future__ import annotations

import fitz  # PyMuPDF
from PIL import Image


def pdf_to_images(pdf_path: str, *, dpi: int = 150) -> list[Image.Image]:
    """Rasterize each PDF page to a PIL image for MiniCPM-V."""
    doc = fitz.open(pdf_path)
    images: list[Image.Image] = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        images.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    return images
