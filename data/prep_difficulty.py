"""Objective 2 — difficulty-classification training data.

Uses NCERT_Dataset's Difficulty column as free labels. ~1k rows.
The model learns: Class + Subject + question text → Easy / Medium / Hard.

Run: python -m data.prep_difficulty
"""
from __future__ import annotations

import json
import os
import random

from data.prep_generation import _SCOPE_SUBJECTS, find_col

OUT = "data/processed/difficulty.jsonl"
TARGET = 1000
SEED = 43
_VALID_LEVELS = {"Easy", "Medium", "Hard"}


def build() -> None:
    from datasets import load_dataset
    from config import CONFIG

    os.makedirs("data/processed", exist_ok=True)

    print("Loading ParthKadam2003/NCERT_Dataset (difficulty labels)...")
    ds = load_dataset("ParthKadam2003/NCERT_Dataset", split="train")
    cols = ds.column_names

    col = {
        "grade":      find_col(cols, "grade"),
        "subject":    find_col(cols, "subject"),
        "question":   find_col(cols, "question"),
        "difficulty": find_col(cols, "difficulty"),
    }

    if not col["question"] or not col["difficulty"]:
        raise RuntimeError(f"Cannot find question/difficulty columns. Have: {cols}")

    scope_classes = {str(c) for c in CONFIG.classes}

    filtered = []
    for row in ds:
        grade = str(row.get(col["grade"], "")).strip() if col["grade"] else ""
        if col["grade"] and grade not in scope_classes:
            continue
        subj = str(row.get(col["subject"], "")).lower().strip() if col["subject"] else ""
        if col["subject"] and not any(s in subj for s in _SCOPE_SUBJECTS):
            continue
        diff = str(row.get(col["difficulty"], "")).strip()
        if diff not in _VALID_LEVELS:
            continue
        filtered.append(row)

    print(f"  {len(filtered)} rows with valid difficulty labels after scope filter")

    random.seed(SEED)
    random.shuffle(filtered)

    written = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for row in filtered:
            if written >= TARGET:
                break
            grade   = str(row.get(col["grade"], "8")).strip() if col["grade"] else "8"
            subject = str(row.get(col["subject"], "Science")).strip() if col["subject"] else "Science"
            question = str(row.get(col["question"], "")).strip()
            diff     = str(row.get(col["difficulty"], "")).strip()

            if not question or not diff:
                continue

            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You classify the difficulty of Indian CBSE exam questions "
                            "for Classes 6-10 as Easy, Medium, or Hard. "
                            "Reply with only the label — nothing else."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Classify difficulty for this Class {grade} {subject} question:\n"
                            f"{question}"
                        ),
                    },
                    {"role": "assistant", "content": diff},
                ]
            }
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            written += 1

    print(f"  Wrote {written} examples → {OUT}")


if __name__ == "__main__":
    build()
