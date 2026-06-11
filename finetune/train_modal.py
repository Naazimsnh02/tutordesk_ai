"""Fine-tune Qwen3-4B on Modal (claims Modal + Well-Tuned + Tiny Titan).

Combines the three ChatML datasets (generation, difficulty, grading), runs LoRA SFT
on a Modal GPU, merges the adapter, exports GGUF, and pushes to the HF Hub.

Run:  modal run finetune/train_modal.py
"""
from __future__ import annotations

# import modal
from finetune.lora_config import LORA

DATASETS = [
    "data/processed/generation.jsonl",
    "data/processed/difficulty.jsonl",
    "data/processed/grading.jsonl",
]


def train() -> None:
    """TODO Phase 3:
    - define a modal.App + GPU image (transformers, peft, trl)
    - load + concat DATASETS, apply Qwen chat template
    - LoRA SFT with LORA hyperparameters
    - merge adapter -> push to HF Hub (CONFIG.qwen_finetuned_model)
    - export GGUF for llama.cpp (Off-the-Grid)
    """
    raise NotImplementedError("Phase 3: implement Modal training job")


if __name__ == "__main__":
    train()
