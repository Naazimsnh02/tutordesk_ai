"""Objective 2 — difficulty classification training data.

Uses NCERT_Dataset's `Difficulty` column as free labels. ~1k rows.
"""
from __future__ import annotations

OUT = "data/processed/difficulty.jsonl"


def build() -> None:
    """TODO Phase 3:
    For each sampled row -> ChatML:
        user:   "Classify difficulty (Easy/Medium/Hard) for this Class {Grade} question: {Question}"
        assistant: "{Difficulty} - {one-line reason}"
    """
    raise NotImplementedError("Phase 3: implement difficulty data prep")


if __name__ == "__main__":
    build()
