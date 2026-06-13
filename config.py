"""Central configuration for TutorDesk AI.

Reads environment (.env) and exposes typed settings used across the app.
Keep all model IDs, toggles, and scope constants here so phases stay consistent.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "1" if default else "0") == "1"


@dataclass(frozen=True)
class Config:
    # --- Secrets ---
    hf_token: str = os.getenv("HF_TOKEN", "")
    hf_username: str = os.getenv("HF_USERNAME", "")
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")  # fallback only, if Cohere award needs API
    bfl_api_key: str = os.getenv("BFL_API_KEY", "")  # fallback only

    # --- Runtime toggles ---
    offline: bool = _bool("TUTORDESK_OFFLINE")  # Off-the-Grid mode: local models, no Modal
    vision_model_version: str = os.getenv("TUTORDESK_VISION_MODEL", "4.5")

    # --- Off-the-Grid / llama.cpp (Off-Grid + Llama Champion badges) ---
    # Download Qwen3-4B GGUF from https://huggingface.co/Qwen/Qwen3-4B-GGUF and set this.
    qwen_gguf_path: str = os.getenv("QWEN_GGUF_PATH", "")
    # Number of layers to offload to GPU (-1 = all, 0 = CPU-only).
    gguf_n_gpu_layers: int = int(os.getenv("GGUF_N_GPU_LAYERS", "-1"))
    # HF username for dataset/model pushes
    hf_username: str = os.getenv("HF_USERNAME", "naazimsnh02")

    # --- Hosting ---
    # All models are self-hosted as scale-to-zero Modal functions (no external APIs).
    # The HF Space runs only the Gradio UI and calls these by name.
    modal_app_name: str = "tutordesk-ai"

    # --- Model IDs (all open-weight, self-hosted on Modal) ---
    qwen_base_model: str = "Qwen/Qwen3-4B"
    # After Phase 3: set QWEN_FINETUNED_MODEL in .env; serving/modal_app.py reads it.
    qwen_finetuned_model: str = os.getenv("QWEN_FINETUNED_MODEL", "Qwen/Qwen3-4B")
    minicpm_model_45: str = "openbmb/MiniCPM-V-4_5"  # 8B, accurate default
    minicpm_model_46: str = "openbmb/MiniCPM-V-4.6"  # 1.3B, lightweight fallback
    aya_model: str = "CohereLabs/tiny-aya-fire"  # 3.35B, South-Asian-tuned (Cohere claim)
    flux_model: str = "black-forest-labs/FLUX.1-schnell"  # Apache-2.0 (BFL claim)

    # --- Hackathon scope (do not broaden without flagging) ---
    classes: tuple[int, ...] = (6, 7, 8, 9, 10)
    subjects: tuple[str, ...] = ("Mathematics", "Science")
    board: str = "CBSE"
    languages: tuple[str, ...] = ("English", "Hindi", "Tamil")

    @property
    def minicpm_model(self) -> str:
        return self.minicpm_model_46 if self.vision_model_version == "4.6" else self.minicpm_model_45


CONFIG = Config()
