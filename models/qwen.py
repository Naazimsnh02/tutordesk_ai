"""Qwen3-4B client.

Cloud (default): calls the deployed Modal Qwen function.
Offline: loads GGUF locally via llama-cpp-python (Llama Champion / Off-Grid).
Phase 3 will set CONFIG.qwen_finetuned_model and pass it as model_id.
"""
from __future__ import annotations

from functools import lru_cache

from config import CONFIG


@lru_cache(maxsize=1)
def _remote_handle():
    import modal

    Qwen = modal.Cls.from_name(CONFIG.modal_app_name, "Qwen")
    return Qwen()


@lru_cache(maxsize=1)
def _local_handle():
    """llama-cpp-python GGUF loader for offline mode. TODO Off-Grid."""
    raise NotImplementedError("Off-Grid: implement local Qwen via llama-cpp-python")


def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    if CONFIG.offline:
        return _local_handle().generate(system_prompt, user_prompt, max_new_tokens, temperature)
    return _remote_handle().generate.remote(
        system_prompt, user_prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
    )
