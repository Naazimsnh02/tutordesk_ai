"""Objective 1 — question-generation training data.

Loads ParthKadam2003/NCERT_Dataset (MIT), filters to scope (Classes 6-10,
Math/Science), and emits ChatML JSONL for Qwen3-4B SFT.

Run: python -m data.prep_generation
"""
from __future__ import annotations

import json
import os
import random

OUT = "data/processed/generation.jsonl"
TARGET = 3000
SEED = 42

# Flexible column detection — the dataset may use different casing/names.
_COL_VARIANTS: dict[str, list[str]] = {
    "grade":      ["Grade", "Class", "grade", "class", "GRADE", "CLASS"],
    "subject":    ["Subject", "subject", "SUBJECT"],
    "topic":      ["Topic", "Chapter", "topic", "chapter", "TOPIC", "CHAPTER"],
    "question":   ["Question", "question", "Q", "QUESTION"],
    "answer":     ["Answer", "answer", "A", "Solution", "solution",
                   "Answer_Explanation", "answer_explanation"],
    "difficulty": ["Difficulty", "difficulty", "Level", "level",
                   "Difficulty_Level", "difficulty_level"],
    "qtype":      ["QuestionType", "Question_Type", "question_type",
                   "Type", "type", "TYPE"],
}

_SCOPE_SUBJECTS = {"mathematics", "maths", "math", "science"}


def find_col(columns: list[str], key: str) -> str | None:
    for v in _COL_VARIANTS[key]:
        if v in columns:
            return v
    return None


def _in_scope(row: dict, col_grade: str | None, col_subject: str | None,
              scope_classes: set[str]) -> bool:
    if col_grade and str(row.get(col_grade, "")).strip() not in scope_classes:
        return False
    if col_subject:
        subj = str(row.get(col_subject, "")).lower().strip()
        if not any(s in subj for s in _SCOPE_SUBJECTS):
            return False
    return True


def _to_chatml(row: dict, col: dict[str, str | None]) -> dict | None:
    question = str(row.get(col["question"], "")).strip()
    answer   = str(row.get(col["answer"],   "")).strip()
    if not question or not answer:
        return None

    grade      = str(row.get(col["grade"],   "8")) if col["grade"] else "8"
    subject    = str(row.get(col["subject"], "Science")) if col["subject"] else "Science"
    topic      = str(row.get(col["topic"],   "")) if col["topic"] else ""
    difficulty = str(row.get(col["difficulty"], "Medium")) if col["difficulty"] else "Medium"
    qtype      = str(row.get(col["qtype"], "Short Answer")) if col["qtype"] else "Short Answer"

    topic_clause = f" on the topic '{topic}'" if topic else ""
    return {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert Indian CBSE tutor for Classes 6-10 Math and Science. "
                    "Generate exam-style questions with clear answers and step-by-step explanations."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate a {difficulty} {qtype} question for Class {grade} {subject}"
                    f"{topic_clause}. Provide the full question, answer, and explanation."
                ),
            },
            {
                "role": "assistant",
                "content": f"Question: {question}\n\nAnswer: {answer}",
            },
        ]
    }


def build() -> None:
    from datasets import load_dataset
    from config import CONFIG

    os.makedirs("data/processed", exist_ok=True)

    print("Loading ParthKadam2003/NCERT_Dataset...")
    ds = load_dataset("ParthKadam2003/NCERT_Dataset", split="train")
    cols = ds.column_names
    print(f"  {len(ds)} rows · columns: {cols}")

    col = {k: find_col(cols, k) for k in _COL_VARIANTS}
    print(f"  Column map: {col}")

    if not col["question"] or not col["answer"]:
        raise RuntimeError(f"Cannot find question/answer columns. Have: {cols}")

    scope_classes = {str(c) for c in CONFIG.classes}

    filtered = [
        row for row in ds
        if _in_scope(row, col["grade"], col["subject"], scope_classes)
    ]
    print(f"  {len(filtered)} rows after scope filter")

    random.seed(SEED)
    random.shuffle(filtered)

    written = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for row in filtered:
            if written >= TARGET:
                break
            example = _to_chatml(row, col)
            if example:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
                written += 1

    print(f"  Wrote {written} examples → {OUT}")


if __name__ == "__main__":
    build()
