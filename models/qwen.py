"""Qwen3-4B client.

Cloud (default): calls the deployed Modal Qwen function.
Offline (TUTORDESK_OFFLINE=1): loads the fine-tuned GGUF locally via llama-cpp-python.
  - Set QWEN_GGUF_PATH to the local .gguf file (Qwen/Qwen3-4B-GGUF or fine-tuned export).
  - Set GGUF_N_GPU_LAYERS=-1 to offload all layers to GPU (default), 0 for CPU-only.
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
def _local_llm():
    """Load the GGUF model via llama-cpp-python for Off-the-Grid mode."""
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError(
            "llama-cpp-python is not installed. "
            "Run: pip install llama-cpp-python"
        ) from exc

    path = CONFIG.qwen_gguf_path
    if not path:
        raise RuntimeError(
            "QWEN_GGUF_PATH is not set. "
            "Download Qwen3-4B GGUF from https://huggingface.co/Qwen/Qwen3-4B-GGUF "
            "and set QWEN_GGUF_PATH=/path/to/qwen3-4b-q4_k_m.gguf in .env"
        )

    return Llama(
        model_path=path,
        n_ctx=4096,
        n_gpu_layers=CONFIG.gguf_n_gpu_layers,
        chat_format="chatml",
        verbose=False,
    )


def _generate_local(
    system_prompt: str,
    user_prompt: str,
    max_new_tokens: int,
    temperature: float,
) -> str:
    llm = _local_llm()
    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_new_tokens,
        temperature=temperature,
    )
    return result["choices"][0]["message"]["content"]


def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    if CONFIG.offline:
        return _generate_local(system_prompt, user_prompt, max_new_tokens, temperature)
    return _remote_handle().generate.remote(
        system_prompt, user_prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
    )
