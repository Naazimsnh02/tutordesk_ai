"""LoRA / SFT hyperparameters for the Qwen3-4B fine-tune."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoraConfig:
    base_model: str = "Qwen/Qwen3-4B"
    r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "k_proj", "v_proj", "o_proj")
    learning_rate: float = 2e-4
    epochs: int = 3
    max_seq_len: int = 2048
    batch_size: int = 4
    grad_accum: int = 4


LORA = LoraConfig()
