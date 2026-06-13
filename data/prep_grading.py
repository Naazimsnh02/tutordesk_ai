"""Objective 3 — Indian-style grading training data (synthesized).

For each source Q&A pair we ask the deployed Qwen model to generate:
  - a step-mark marking scheme
  - 4 simulated student answers (correct / right-answer-no-working / partial / wrong-method)
  - marks + per-step feedback for each

Each Q&A pair expands to 4 ChatML training examples (one per student answer type).
Source: ~150 filtered rows from NCERT_Dataset → ~600 grading examples.

Uses Modal starmap to parallelize synthesis across containers (~5-10 min total).

Run: python -m data.prep_grading
"""
from __future__ import annotations

import json
import os
import random
import re

from data.prep_generation import _SCOPE_SUBJECTS, find_col

OUT = "data/processed/grading.jsonl"
SOURCE_ROWS = 150
SEED = 44

_GRADING_SYSTEM = (
    "You are an expert Indian CBSE teacher creating grading training data. "
    "Given a question and correct answer, output a JSON object with:\n"
    '- "marking_scheme": list of 3-5 step strings, each worth 1 mark\n'
    '- "total_marks": integer (3-5)\n'
    '- "examples": list of 4 objects, one per student type:\n'
    '  Each object: {"type": "correct|no_working|partial|wrong_method", '
    '"student_answer": "...", "marks": N, "feedback": "one sentence"}\n'
    "Output ONLY valid JSON, no explanation or markdown fences."
)


def _make_prompt(question: str, answer: str, grade: str, subject: str) -> str:
    return (
        f"Class {grade} {subject} question:\n{question}\n\n"
        f"Correct answer: {answer}\n\n"
        "Generate the grading example JSON."
    )


def _parse_response(raw: str) -> dict | None:
    raw = raw.strip()
    # Strip markdown fences if Qwen wraps in ```json ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try extracting the first {...} block
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                return None
    return None


def _to_chatml_examples(qa: dict, parsed: dict) -> list[dict]:
    """Convert one synthesized grading object into N ChatML training examples."""
    question = qa["question"]
    scheme = "\n".join(
        f"  Step {i+1}: {s}" for i, s in enumerate(parsed.get("marking_scheme", []))
    )
    total = parsed.get("total_marks", len(parsed.get("marking_scheme", [])))
    examples = []
    for ex in parsed.get("examples", []):
        student_ans = ex.get("student_answer", "")
        marks = ex.get("marks", 0)
        feedback = ex.get("feedback", "")
        if not student_ans:
            continue
        example = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an Indian CBSE teacher grading student answers. "
                        "Award step marks, give partial credit where deserved, "
                        "and provide a one-sentence feedback comment."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Grade out of {total} marks.\n\n"
                        f"Question: {question}\n\n"
                        f"Marking scheme:\n{scheme}\n\n"
                        f"Student answer: {student_ans}"
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        f"Marks: {marks}/{total}\n"
                        f"Feedback: {feedback}"
                    ),
                },
            ]
        }
        examples.append(example)
    return examples


def build(source_rows: int = SOURCE_ROWS) -> None:
    from datasets import load_dataset
    import modal
    from config import CONFIG

    os.makedirs("data/processed", exist_ok=True)

    print("Loading source Q&A pairs from NCERT_Dataset...")
    ds = load_dataset("ParthKadam2003/NCERT_Dataset", split="train")
    cols = ds.column_names

    col = {
        "grade":    find_col(cols, "grade"),
        "subject":  find_col(cols, "subject"),
        "question": find_col(cols, "question"),
        "answer":   find_col(cols, "answer"),
    }
    if not col["question"] or not col["answer"]:
        raise RuntimeError(f"Cannot find question/answer columns. Have: {cols}")

    scope_classes = {str(c) for c in CONFIG.classes}
    filtered = []
    for row in ds:
        if col["grade"] and str(row.get(col["grade"], "")).strip() not in scope_classes:
            continue
        if col["subject"]:
            subj = str(row.get(col["subject"], "")).lower().strip()
            if not any(s in subj for s in _SCOPE_SUBJECTS):
                continue
        q = str(row.get(col["question"], "")).strip()
        a = str(row.get(col["answer"], "")).strip()
        if q and a and len(a) > 20:  # skip trivially short answers
            filtered.append({
                "question": q,
                "answer": a,
                "grade": str(row.get(col["grade"], "8")) if col["grade"] else "8",
                "subject": str(row.get(col["subject"], "Science")) if col["subject"] else "Science",
            })

    random.seed(SEED)
    random.shuffle(filtered)
    source = filtered[:source_rows]
    print(f"  Synthesizing grading examples for {len(source)} Q&A pairs via Modal Qwen...")

    # Build prompt tuples for starmap — positional args match Qwen.generate signature
    prompt_tuples = [
        (_GRADING_SYSTEM, _make_prompt(qa["question"], qa["answer"], qa["grade"], qa["subject"]))
        for qa in source
    ]

    # Parallel synthesis via the deployed Qwen endpoint
    Qwen = modal.Cls.from_name(CONFIG.modal_app_name, "Qwen")
    qwen = Qwen()
    raw_responses = list(
        qwen.generate.starmap(prompt_tuples, kwargs={"max_new_tokens": 600, "temperature": 0.3})
    )

    written = 0
    parse_failures = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for qa, raw in zip(source, raw_responses):
            parsed = _parse_response(raw)
            if not parsed:
                parse_failures += 1
                continue
            for example in _to_chatml_examples(qa, parsed):
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
                written += 1

    print(f"  Wrote {written} grading examples → {OUT}  ({parse_failures} parse failures)")


if __name__ == "__main__":
    build()
