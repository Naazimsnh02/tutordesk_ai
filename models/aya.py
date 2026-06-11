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
    """TODO Phase 5: return Modal TinyAya handle."""
    raise NotImplementedError("Phase 5: wire Tiny Aya backend")


def localize(text: str, *, language: str) -> str:
    if language.lower() == "english" or not text:
        return text
    if CONFIG.offline:
        return text  # graceful fallback: keep English when fully local
    return _backend().localize(text, language=language)
