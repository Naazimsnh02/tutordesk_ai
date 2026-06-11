"""Objective 1 — question/content generation training data.

Load ParthKadam2003/NCERT_Dataset (MIT), filter to scope (Classes 6-10, Math/Science),
and emit ChatML JSONL for Qwen3-4B SFT. Near-free: templates existing columns.
"""
from __future__ import annotations

import json

# from datasets import load_dataset
from config import CONFIG

OUT = "data/processed/generation.jsonl"


def build() -> None:
    """TODO Phase 3:
    ds = load_dataset("ParthKadam2003/NCERT_Dataset", split="train")
    filter Grade in CONFIG.classes and Subject in CONFIG.subjects
    for each row -> ChatML:
        system: "You are an Indian CBSE tutor."
        user:   "Generate a {Difficulty} {QuestionType} question for Class {Grade}
                 {Subject} on '{Topic}'. Provide the answer."
        assistant: "{Question}\nAnswer: {Answer}\nExplanation: {Explanation}"
    Sample ~3-5k rows. Write JSONL of {"messages": [...]}.
    """
    raise NotImplementedError("Phase 3: implement generation data prep")


if __name__ == "__main__":
    build()
