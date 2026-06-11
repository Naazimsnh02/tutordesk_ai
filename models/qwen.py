"""Qwen3-4B client — generation + Indian-style grading.

Cloud mode (default): calls the Modal `Qwen` function (serving/modal_app.py).
Offline mode (CONFIG.offline): loads the merged GGUF locally via llama.cpp (Llama Champion).

Phase 1 uses the base model; Phase 3 swaps in the fine-tuned model.
"""
from __future__ import annotations

from functools import lru_cache

from config import CONFIG


@lru_cache(maxsize=1)
def _remote():
    """Handle to the deployed Modal Qwen function. TODO Phase 1.

    import modal
    return modal.Cls.from_name(CONFIG.modal_app_name, "Qwen")()
    """
    raise NotImplementedError("Phase 1: wire Modal Qwen function")


@lru_cache(maxsize=1)
def _local():
    """Local llama.cpp GGUF loader for offline mode. TODO Off-Grid."""
    raise NotImplementedError("Off-Grid: implement local Qwen via llama.cpp")


def generate(system_prompt: str, user_prompt: str, *, max_new_tokens: int = 1024, temperature: float = 0.7) -> str:
    backend = _local() if CONFIG.offline else _remote()
    return backend.generate(system_prompt, user_prompt, max_new_tokens=max_new_tokens, temperature=temperature)
