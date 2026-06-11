"""Grader agent — Indian-style marking (Feature 5).

Grades a student's answers (already extracted from the answer sheet by MiniCPM-V)
against a marking scheme, applying CBSE/state-board conventions: step marks,
partial credit, method marks. Powered by the fine-tuned Qwen3-4B grading objective.
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You are an experienced Indian examiner. Grade the student's answer against the marking "
    "scheme. Award step marks and partial credit as a CBSE examiner would. Return marks, a "
    "per-step breakdown, and brief feedback."
)

agent = Agent(name="grader", system_prompt=SYSTEM)


def grade(question: str, marking_scheme: str, student_answer: str, *, marks: int) -> str:
    prompt = (
        f"Grade out of {marks}.\nQuestion: {question}\n"
        f"Marking scheme: {marking_scheme}\nStudent answer: {student_answer}"
    )
    return agent.run(prompt)
