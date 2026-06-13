"""Tiny Aya client — regional-language generation (Feature 3, Cohere claim).

Self-hosted on Modal (CohereLabs/tiny-aya-fire, 3.35B, South-Asian-tuned). Renders any
artifact into the teacher's selected language. English passes through unchanged.

NOTE: if the Cohere award turns out to require the hosted Cohere API, swap _backend()
to a Cohere API call (CONFIG.cohere_api_key) — the interface stays the same.
"""
from __future__ import annotations

from functools import lru_cache

from config import CONFIG


@lru_cache(maxsize=1)
def _backend():
    import modal

    TinyAya = modal.Cls.from_name(CONFIG.modal_app_name, "TinyAya")
    return TinyAya()


def localize(text: str, *, language: str) -> str:
    """Translate `text` into `language`. Returns text unchanged if English or offline."""
    if language.lower() == "english" or not text:
        return text
    if CONFIG.offline:
        return text  # graceful degradation: English-only in Off-the-Grid mode
    return _backend().localize.remote(text, language)
