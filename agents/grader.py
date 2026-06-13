"""Grader agent — Indian-style marking (Feature 5).

Grades a student's answers (already extracted from the answer sheet by MiniCPM-V)
against a marking scheme, applying CBSE/state-board conventions: step marks,
partial credit, method marks. Powered by the fine-tuned Qwen3-4B grading objective.

Output contract: every grade() call must begin with "MARKS: X/Y" so extract_score()
can parse it reliably without LLM fragility.
"""
from __future__ import annotations

import json
import re

from agents.base import Agent

SYSTEM = (
    "You are an experienced Indian examiner grading CBSE Class 6–10 answers. "
    "Apply step marks and partial credit exactly as a CBSE examiner would.\n"
    "Always begin your response with:\n"
    "MARKS: <awarded>/<total>\n"
    "Then write BREAKDOWN: and give a brief per-step analysis.\n"
    "Then write FEEDBACK: and give one encouraging sentence."
)

_PARSE_SYSTEM = (
    "You parse marking schemes into JSON. "
    "Return ONLY a valid JSON array, no prose, no code fences."
)

agent = Agent(name="grader", system_prompt=SYSTEM)
_parse_agent = Agent(name="grader_parser", system_prompt=_PARSE_SYSTEM)


def grade(question: str, marking_scheme: str, student_answer: str, *, marks: int) -> str:
    """Grade one question. Output always starts with 'MARKS: X/{marks}'."""
    prompt = (
        f"Grade out of {marks}.\n"
        f"Question: {question}\n"
        f"Marking scheme: {marking_scheme}\n"
        f"Student answer: {student_answer}"
    )
    return agent.run(prompt)


def extract_score(text: str, max_marks: int) -> int:
    """Parse the awarded marks from a grade() output. Falls back to 0 on failure."""
    m = re.search(r"MARKS:\s*(\d+)\s*/\s*\d+", text)
    if m:
        return min(int(m.group(1)), max_marks)
    # Secondary fallback: any "X/max_marks" pattern
    m = re.search(rf"(\d+)\s*/\s*{max_marks}", text)
    if m:
        return min(int(m.group(1)), max_marks)
    return 0


def parse_scheme(raw: str) -> list[dict]:
    """Parse a marking scheme text into [{q, marks, answer}, ...].

    Tries a deterministic regex first (fast, reliable for the provided template).
    Falls back to Qwen for free-form input; falls back further to a single-question
    wrap if both fail.
    """
    items = _regex_parse(raw)
    if items:
        return items

    # Qwen fallback for free-form schemes
    prompt = (
        'Parse into a JSON array. Each element must be:\n'
        '{"q": <question number int>, "marks": <marks int>, "answer": <model answer string>}\n\n'
        f"Marking scheme:\n{raw}"
    )
    try:
        result = _parse_agent.run(prompt, temperature=0.1, max_new_tokens=1024)
        match = re.search(r"\[.*?\]", result, re.DOTALL)
        if match:
            items = json.loads(match.group())
            if items and all("q" in i and "marks" in i and "answer" in i for i in items):
                return items
    except (json.JSONDecodeError, Exception):
        pass

    # Last resort: treat entire scheme as one question
    marks_m = re.search(r"(\d+)\s*marks?", raw, re.IGNORECASE)
    total = int(marks_m.group(1)) if marks_m else 10
    return [{"q": 1, "marks": total, "answer": raw}]


def _regex_parse(raw: str) -> list[dict]:
    """Parse the teacher template format: 'Q1 [N marks]: ...'"""
    pattern = re.compile(
        r"Q(\d+)\s*\[(\d+)\s*marks?\]\s*:(.*?)(?=\nQ\d+\s*\[|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    items = []
    for m in pattern.finditer(raw):
        items.append({
            "q": int(m.group(1)),
            "marks": int(m.group(2)),
            "answer": m.group(3).strip(),
        })
    return items
