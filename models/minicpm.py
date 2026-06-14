"""MiniCPM-V client — reads textbook pages & answer sheets (OpenBMB).

Cloud mode: calls the Modal `MiniCPM` function.
Offline: raises NotImplementedError (MiniCPM-V is too large for most laptops; Off-Grid
         uses text-only flow instead — callers must handle the fallback).
"""
from __future__ import annotations

import io
from functools import lru_cache

from PIL import Image

from config import CONFIG


@lru_cache(maxsize=1)
def _remote_handle():
    import modal

    MiniCPM = modal.Cls.from_name(CONFIG.modal_app_name, "MiniCPM")
    return MiniCPM()


def read_image(image: Image.Image, instruction: str) -> str:
    """Run a vision instruction over a PIL image and return the model response.

    Used by worksheet_from_textbook (chapter extraction) and auto_grade (answer sheet).
    Serialises the image to PNG bytes for the Modal RPC boundary.
    """
    if CONFIG.offline:
        raise NotImplementedError(
            "MiniCPM-V is not available in offline mode. "
            "Use the Weekly Teaching Pack tab and paste chapter text manually."
        )
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    try:
        return _remote_handle().read_image.remote(buf.getvalue(), instruction)
    except Exception as exc:
        name = type(exc).__name__
        msg = str(exc)
        if "AuthError" in name or "Token missing" in msg or "Could not authenticate" in msg:
            raise RuntimeError(
                "Modal credentials not configured.\n\n"
                "Go to your HF Space → Settings → Variables and secrets → New secret, "
                "and add MODAL_TOKEN_ID and MODAL_TOKEN_SECRET from modal.com/settings."
            ) from exc
        raise
